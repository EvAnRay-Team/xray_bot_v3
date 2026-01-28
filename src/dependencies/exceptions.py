class UnsupportedAdapterError(ValueError):
    def __init__(self, adapter: str) -> None:
        super().__init__(f"Unsupported adapter: {adapter}")
