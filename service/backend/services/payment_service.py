"""
Mock payment service simulating a Stripe-like payment gateway.

This is a simulation only — no real money is processed.

Test card numbers:
  - 4242424242424242  → Always succeeds
  - 4000000000000002  → Always fails (card declined)
  - 4000000000000077  → Always returns pending
  - Any other valid-length number → 90% success rate (randomized)
"""
import uuid
import random
from models.payment import PaymentRequest, PaymentResponse


class PaymentService:
    """Simulates payment gateway behavior without real API calls."""

    # Deterministic test cards
    _ALWAYS_FAIL = {"4000000000000002"}
    _ALWAYS_PENDING = {"4000000000000077"}
    _ALWAYS_SUCCESS = {"4242424242424242"}

    def process_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Process a payment request through the mock gateway.

        Validates card format, then routes to the appropriate simulated outcome.

        Returns:
            PaymentResponse with status 'success', 'failure', or 'pending'.
        """
        card = request.card_number.replace(" ", "").replace("-", "")

        # Basic card number validation
        if not card.isdigit() or len(card) < 13 or len(card) > 19:
            return PaymentResponse(
                success=False,
                status="failure",
                message="Invalid card number format"
            )

        # Expiry format validation (MM/YY)
        if "/" not in request.expiry or len(request.expiry) != 5:
            return PaymentResponse(
                success=False,
                status="failure",
                message="Invalid expiry date format. Use MM/YY"
            )

        # CVV validation
        if not request.cvv.isdigit() or len(request.cvv) not in (3, 4):
            return PaymentResponse(
                success=False,
                status="failure",
                message="Invalid CVV"
            )

        # Route to deterministic test card outcomes
        if card in self._ALWAYS_FAIL:
            return PaymentResponse(
                success=False,
                status="failure",
                message="Card declined by issuing bank"
            )

        if card in self._ALWAYS_PENDING:
            return PaymentResponse(
                success=False,
                transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                status="pending",
                message="Payment is under review. You will be notified shortly."
            )

        if card in self._ALWAYS_SUCCESS:
            return self._build_success()

        # Randomized outcome for unrecognized cards (90% success)
        if random.random() < 0.9:
            return self._build_success()

        return PaymentResponse(
            success=False,
            status="failure",
            message="Payment failed. Please try a different card or contact your bank."
        )

    def _build_success(self) -> PaymentResponse:
        """Create a successful payment response with a mock transaction ID."""
        return PaymentResponse(
            success=True,
            transaction_id=f"txn_{uuid.uuid4().hex[:16]}",
            status="success",
            message="Payment processed successfully. Thank you for your purchase!"
        )
