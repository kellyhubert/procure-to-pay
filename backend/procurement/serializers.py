from rest_framework import serializers
from .models import User, PurchaseRequest, Approval


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'department')
        read_only_fields = ('id',)


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role', 'phone_number', 'department')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ApprovalSerializer(serializers.ModelSerializer):
    approver = UserSerializer(read_only=True)
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)

    class Meta:
        model = Approval
        fields = ('id', 'purchase_request', 'approver', 'approver_name', 'approved', 'comments', 'approved_at')
        read_only_fields = ('id', 'purchase_request', 'approved_at')


class PurchaseRequestSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    approvals = ApprovalSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = PurchaseRequest
        fields = (
            'id', 'title', 'description', 'amount', 'status',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'proforma', 'proforma_data',
            'purchase_order', 'purchase_order_data',
            'receipt', 'receipt_data', 'receipt_validation',
            'rejection_reason', 'approvals'
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at', 'purchase_order',
                           'purchase_order_data', 'receipt_data', 'receipt_validation')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PurchaseRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = ('title', 'description', 'amount', 'proforma')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PurchaseRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseRequest
        fields = ('title', 'description', 'amount', 'proforma')

    def validate(self, attrs):
        if self.instance.status != 'pending':
            raise serializers.ValidationError("Cannot update non-pending requests")
        if self.instance.created_by != self.context['request'].user:
            raise serializers.ValidationError("You can only update your own requests")
        return attrs


class ApprovalActionSerializer(serializers.Serializer):
    approved = serializers.BooleanField(required=True)
    comments = serializers.CharField(required=False, allow_blank=True)


class ReceiptSubmissionSerializer(serializers.Serializer):
    receipt = serializers.FileField(required=True)
