# Chapa Payment Integration Setup Guide

## Prerequisites

1. Python 3.8+
2. Django 3.2+
3. Redis (for Celery)
4. Chapa account with API keys

## Step 1: Install Dependencies

```bash
pip install django djangorestframework celery redis requests python-dotenv
```

## Step 2: Get Chapa API Keys

1. Sign up at https://developer.chapa.co/
2. Navigate to your dashboard
3. Get your **Secret Key** from the API Keys section
4. For testing, use the **Sandbox** environment

## Step 3: Project Setup

### 3.1 Create .env file

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Chapa credentials:

```
CHAPA_SECRET_KEY=CHASECK_TEST-xxxxxxxxxxxxxxxxxxxxxxxx
CHAPA_SANDBOX=True
```

### 3.2 Update __init__.py

In `alx_travel_app_0x02/__init__.py`, add:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 3.3 Create services directory

```bash
mkdir -p listings/services
touch listings/services/__init__.py
```
### 3.4 Create templates directory

```bash
mkdir -p templates/emails
```

## Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Step 5: Start Services

### Terminal 1: Django Server
```bash
python manage.py runserver
```

### Terminal 2: Redis Server
```bash
redis-server
```

### Terminal 3: Celery Worker
```bash
celery -A alx_travel_app_0x02 worker --loglevel=info
```

## Step 6: Testing the Integration

### 6.1 Create a Test Booking

First, create a booking using Django admin or shell:

```python
python manage.py shell

from listings.models import Booking
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()  # or create a user

booking = Booking.objects.create(
    user=user,
    total_amount=1000.00,
    status='pending'
)
print(f"Booking ID: {booking.id}")
```

### 6.2 Test Payment Initiation

**Request:**
```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "YOUR_BOOKING_UUID",
    "return_url": "http://localhost:8000/api/payments/success/"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Payment initialized successfully",
  "payment": {
    "id": "uuid",
    "booking_id": "uuid",
    "amount": "1000.00",
    "status": "pending",
    "chapa_reference": "TX-XXXXXXXXXXXX",
    "checkout_url": "https://checkout.chapa.co/checkout/payment/..."
  },
  "checkout_url": "https://checkout.chapa.co/checkout/payment/..."
}
```

### 6.3 Complete Payment

1. Open the `checkout_url` in your browser
2. Use Chapa test card details:
   - **Card Number:** 5200 0000 0000 0015
   - **Expiry:** Any future date
   - **CVV:** Any 3 digits
3. Complete the payment

### 6.4 Verify Payment

**Request:**
```bash
curl -X GET http://localhost:8000/api/payments/verify/TX-XXXXXXXXXXXX/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN"
```

**Expected Response:**
```json
{
  "success": true,
  "payment": {
    "id": "uuid",
    "status": "completed",
    "transaction_id": "chapa_transaction_id"
  },
  "verification_data": {
    "status": "success",
    "amount": 1000,
    "currency": "ETB"
  }
}
```

### 6.5 Check Payment Status

**Request:**
```bash
curl -X GET http://localhost:8000/api/payments/{payment_id}/status/ \
  -H "Authorization: Token YOUR_AUTH_TOKEN"
```

## Step 7: Test Chapa Webhook (Callback)

Chapa will automatically call your callback URL when payment is completed.

**Callback URL:** `http://your-domain.com/api/payments/callback/`

For local testing, use ngrok:

```bash
ngrok http 8000
```

Update your callback URL in the payment initiation to use the ngrok URL.

## Step 8: Monitor Logs

### Django Logs
Check `payment_logs.log` file for payment processing logs.

### Celery Logs
Check the celery worker terminal for email task execution.

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Celery tasks not executing

**Solution:**
1. Ensure Redis is running: `redis-cli ping` (should return PONG)
2. Restart celery worker
3. Check celery logs for errors

### Issue: Emails not sending

**Solution:**
1. Verify email settings in `.env`
2. For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
3. Check celery worker logs

### Issue: Payment verification fails

**Solution:**
1. Verify CHAPA_SECRET_KEY is correct
2. Check if using correct environment (sandbox vs production)
3. Verify transaction reference is correct

## Production Deployment Checklist

- [ ] Set `CHAPA_SANDBOX=False`
- [ ] Use production Chapa API keys
- [ ] Set up SSL certificate for callback URL
- [ ] Configure proper email service (e.g., SendGrid, Mailgun)
- [ ] Set up monitoring and logging
- [ ] Configure Redis with persistence
- [ ] Set up Celery with supervisor/systemd
- [ ] Add rate limiting to API endpoints
- [ ] Implement proper error tracking (e.g., Sentry)

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/payments/initiate/` | POST | Initialize a new payment |
| `/api/payments/callback/` | GET/POST | Chapa callback handler |
| `/api/payments/verify/<tx_ref>/` | GET | Manually verify payment |
| `/api/payments/<id>/status/` | GET | Get payment status |
| `/api/payments/success/` | GET | Payment success redirect page |

## Testing Checklist

- [ ] Payment initialization works
- [ ] Checkout URL is generated
- [ ] Payment can be completed in sandbox
- [ ] Callback is received and processed
- [ ] Payment status is updated correctly
- [ ] Booking status changes to confirmed
- [ ] Confirmation email is sent
- [ ] Manual verification works
- [ ] Failed payment handling works
- [ ] Error cases are handled gracefully

## Support

For Chapa API issues:
- Documentation: https://developer.chapa.co/docs
- Support: support@chapa.co

For integration issues:
- Check logs in `payment_logs.log`
- Review Celery worker output
- Test in sandbox environment first