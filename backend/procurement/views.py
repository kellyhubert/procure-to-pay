from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db import transaction, models
from django.utils import timezone
from .models import User, PurchaseRequest, Approval
from .serializers import (
    UserSerializer, UserRegistrationSerializer,
    PurchaseRequestSerializer, PurchaseRequestCreateSerializer,
    PurchaseRequestUpdateSerializer, ApprovalSerializer,
    ApprovalActionSerializer, ReceiptSubmissionSerializer
)
from .permissions import IsStaff, IsApprover, IsFinance, CanEditRequest, CanApproveRequest
from .utils import extract_proforma_data, generate_purchase_order, validate_receipt


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class PurchaseRequestViewSet(viewsets.ModelViewSet):
    queryset = PurchaseRequest.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PurchaseRequestUpdateSerializer
        return PurchaseRequestSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PurchaseRequest.objects.all()

        # Staff can only see their own requests
        if user.role == 'staff':
            queryset = queryset.filter(created_by=user)

        # Approvers can see all pending requests and ones they've reviewed
        elif user.role in ['approver-level-1', 'approver-level-2']:
            queryset = queryset.filter(
                models.Q(status='pending') | models.Q(approvals__approver=user)
            ).distinct()

        # Finance can see all requests
        elif user.role == 'finance':
            queryset = queryset.all()

        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.select_related('created_by').prefetch_related('approvals__approver')

    @transaction.atomic
    def perform_create(self, serializer):
        purchase_request = serializer.save(created_by=self.request.user)

        # Extract proforma data if proforma is uploaded
        if purchase_request.proforma:
            try:
                extracted_data = extract_proforma_data(purchase_request.proforma)
                purchase_request.proforma_data = extracted_data
                purchase_request.save()
            except Exception as e:
                print(f"Error extracting proforma data: {e}")

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, CanApproveRequest])
    @transaction.atomic
    def approve(self, request, pk=None):
        purchase_request = self.get_object()
        serializer = ApprovalActionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check if request is still pending
        if purchase_request.status != 'pending':
            return Response(
                {'error': 'Request is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user role can approve
        if request.user.role not in ['approver-level-1', 'approver-level-2']:
            return Response(
                {'error': 'You do not have permission to approve'},
                status=status.HTTP_403_FORBIDDEN
            )

        approved = serializer.validated_data['approved']
        comments = serializer.validated_data.get('comments', '')

        # Create or update approval
        approval, created = Approval.objects.get_or_create(
            purchase_request=purchase_request,
            approver=request.user
        )
        approval.approved = approved
        approval.comments = comments
        approval.approved_at = timezone.now()
        approval.save()

        # If rejected, update purchase request status
        if not approved:
            purchase_request.status = 'rejected'
            purchase_request.rejection_reason = comments
            purchase_request.save()
            return Response(
                PurchaseRequestSerializer(purchase_request).data,
                status=status.HTTP_200_OK
            )

        # Check if all required approvals are met
        if purchase_request.check_approval_status():
            # All approvals received, generate PO
            try:
                po_file, po_data = generate_purchase_order(purchase_request)
                purchase_request.purchase_order = po_file
                purchase_request.purchase_order_data = po_data
                purchase_request.save()
            except Exception as e:
                print(f"Error generating PO: {e}")

        return Response(
            PurchaseRequestSerializer(purchase_request).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, CanApproveRequest])
    @transaction.atomic
    def reject(self, request, pk=None):
        request_data = request.data.copy()
        request_data['approved'] = False
        request._full_data = request_data
        return self.approve(request, pk)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    @transaction.atomic
    def submit_receipt(self, request, pk=None):
        purchase_request = self.get_object()

        # Check if user owns this request
        if purchase_request.created_by != request.user:
            return Response(
                {'error': 'You can only submit receipts for your own requests'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if request is approved
        if purchase_request.status != 'approved':
            return Response(
                {'error': 'Can only submit receipts for approved requests'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReceiptSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        purchase_request.receipt = serializer.validated_data['receipt']

        # Validate receipt against PO
        try:
            receipt_data, validation_result = validate_receipt(
                purchase_request.receipt,
                purchase_request.purchase_order_data
            )
            purchase_request.receipt_data = receipt_data
            purchase_request.receipt_validation = validation_result
        except Exception as e:
            print(f"Error validating receipt: {e}")
            purchase_request.receipt_validation = {
                'status': 'error',
                'message': str(e)
            }

        purchase_request.save()

        return Response(
            PurchaseRequestSerializer(purchase_request).data,
            status=status.HTTP_200_OK
        )


class ApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['approver-level-1', 'approver-level-2']:
            return Approval.objects.filter(approver=user)
        return Approval.objects.none()
