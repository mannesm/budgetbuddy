from sqlalchemy.orm import declared_attr


class AutoTableNameMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # simple CamelCase -> snake_case
        name = []
        for i, c in enumerate(cls.__name__):
            if c.isupper() and i and not cls.__name__[i - 1].isupper():
                name.append("_")
            name.append(c.lower())
        return "".join(name)
