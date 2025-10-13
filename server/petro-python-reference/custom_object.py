class CustomObject:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name  # This is what will be displayed in the QListWidget

    def __repr__(self):
        return f"CustomObject(name={self.name!r}, description={self.description!r})"
