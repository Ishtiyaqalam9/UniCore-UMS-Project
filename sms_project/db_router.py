class DatabaseRouter:
    """Route each Django app to its assigned relational database."""

    app_database = {
        "student": "mysql",
        "teacher": "postgres",
    }

    def db_for_read(self, model, **hints):
        return self.app_database.get(model._meta.app_label, "default")

    def db_for_write(self, model, **hints):
        return self.app_database.get(model._meta.app_label, "default")

    def allow_relation(self, obj1, obj2, **hints):
        # Cross-database foreign keys are intentionally avoided. Snapshot IDs
        # are used by academic/library records, but ordinary relations inside
        # each database remain allowed.
        db1 = self.app_database.get(obj1._meta.app_label, "default")
        db2 = self.app_database.get(obj2._meta.app_label, "default")
        return db1 == db2

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        target = self.app_database.get(app_label, "default")
        return db == target
