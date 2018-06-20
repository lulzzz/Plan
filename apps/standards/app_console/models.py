from django.db import models
from django.db import connection
from django.db.utils import InternalError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group


class StoredProcedureModel(models.Model):

    # static method to run the procedure
    @staticmethod
    def run_mysql(procedure_name):

        try:
            # create a cursor
            cur = connection.cursor()
            # Execute the stored procedure
            cur.callproc(procedure_name)
            # grab the results
            result = cur.fetchall()
            cur.close()
        except InternalError as e:
            return str(e)

        if result == -500:
            return False
        return True

    @staticmethod
    def run_mssql(procedure_name):

        try:
            cur = connection.cursor()
            cur.execute(procedure_name)
            cur.close()
        except InternalError as e:
            return str(e)

        return True

    class Meta:
        managed = False


class Item(models.Model):
    r"""
    Model for Console master table
    """

    permission_type = models.CharField(max_length=100, choices=[
        ('table', 'Table'),
        ('procedure', 'Procedure'),
        ('rpc', 'RPC')
    ])
    name = models.CharField(unique=True, max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    schema = models.CharField(max_length=100, default='dbo', blank=True, null=True)
    sequence = models.IntegerField(blank=True, null=True, help_text='(for procedure only)')
    duration = models.IntegerField(default=60, blank=True, null=True, help_text='in seconds (for procedure only)')
    start_dt = models.DateTimeField(blank=True, null=True, help_text='(for procedure only)')
    end_dt = models.DateTimeField(blank=True, null=True, help_text='(for procedure only)')
    completion_percentage = models.IntegerField(default=0, blank=True, null=True, help_text='(for procedure only)')
    allows_delete = models.BooleanField(default=True)

    def title(self):
        if self.label is None:
            return self.name
        return self.label

    def __str__(self):
        return self.title()


class GroupPermissions(models.Model):
    r"""
    Model for setting group permissions
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Group permission'
        verbose_name_plural = 'Group permissions'
        unique_together = (('group', 'item'),)

    def __str__(self):
        return self.group.name + ' - ' + self.item.title()

class UserPermissions(models.Model):
    r"""
    Model for setting group permissions
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'User permission'
        verbose_name_plural = 'User permissions'
        unique_together = (('user', 'item'),)

    def __str__(self):
        return self.user.username + ' - ' + self.item.title()
