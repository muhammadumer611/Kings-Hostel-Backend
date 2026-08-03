from datetime import datetime
from uuid import uuid4


class ReceiptGenerator:

    def generate(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d")
        unique = uuid4().hex[:6].upper()

        return f"RCP-{timestamp}-{unique}"