import json

from django.conf import settings as cp
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.utils import IntegrityError
from django.db.utils import OperationalError
from django.urls import reverse_lazy
from django.utils import timezone

from rest_framework import status # To return status codes
from rest_framework.views import APIView
from rest_framework.response import Response

from core import gcbvs
from core import utils
from core import mixins_view
from blocks import views

from .models import UserPermissions
from .models import GroupPermissions
from .models import Item
from .models import StoredProcedureModel


class BaseAPIMixin():

    def get_model_obj(self):
        return None

    def get_serializer_obj(self):
        return None


class MasterTableAPIMixin(APIView, BaseAPIMixin, mixins_view.SecurityModelNameMixin):
    r"""
    View that updates master the master table specified in the request.
    Assuming user group has required permissions.
    """

    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    target_model = Item
    permission_type = 'table'
    model_name = None
    allows_delete = True

    def get(self, request, format=None, **kwargs):
        # Get model name
        self.model_name = self.get_model_name(request.user)

        # Check if user has permissions
        if self.model_name == 401:
            content = {'message': '401 no access authorization'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        # Define model
        model_obj = self.get_model_obj()

        # Define serializer
        serializer_obj = self.get_serializer_obj()

        # Define queryset object
        queryset = model_obj.objects.all()

        # Check if queryset has data
        if queryset.count() == 0:
            return JsonResponse([[]], safe=False)

        # Return serialized data
        serializer = serializer_obj(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, format=None, **kwargs):

        # Catch any unexpected exception
        try:

            # Get model name
            self.model_name = self.get_model_name(request.user)

            # Check if user has permissions
            if self.model_name == 401:
                content = {'message': '401 no access authorization'}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

            # Define model
            model_obj = self.get_model_obj()

            # Check if model allows delete
            self.allows_delete = self.target_model.objects.get(name=self.model_name).allows_delete

            # Define serializer
            serializer_obj = self.get_serializer_obj()

            json_data_raw = json.loads(request.data.get('data'))
            json_data_raw = utils.adjust_dict_key_values(
                json=json_data_raw,
                form_field_names_list=model_obj.get_form_field_names_list(model_obj)
            )
            json_data = utils.get_clean_list_of_dict(json_data_raw)

            # Loop through every dataset (Insert/Update)
            pk = 'id'
            pk_list = list()
            serializer_save_list = list()
            for idx, dataset in enumerate(json_data):

                # Existing instance
                model_pk = utils.xint(dataset.get(pk, None))
                pk_list.append(model_pk)
                if model_obj.objects.filter(pk=model_pk).exists():
                    existing_entry = get_object_or_404(model_obj, pk=model_pk)
                    serializer = serializer_obj(existing_entry, data=dataset)

                # New instance
                else:
                    del dataset[pk]
                    serializer = serializer_obj(data=dataset)

                # Validate data
                if serializer.is_valid():
                    # Insert or update (append to valid list)
                    serializer_save_list.append(serializer)
                else:
                    # Return error message as JSON
                    error_dict = serializer.errors
                    for error_field_name, value in error_dict.items():
                        # Get error field(s)
                        if error_field_name == 'non_field_errors':
                            error_field_label = 'Multiple fields affected'
                        else:
                            error_field_label = model_obj._meta.get_field(error_field_name).verbose_name

                        # Get error message
                        error_field_value = value[0]
                        break
                    return Response({
                        'row': idx,
                        'error_field_label': error_field_label,
                        'error_field_value': error_field_value
                    }, status=status.HTTP_400_BAD_REQUEST)


            # Delete model datasets
            instances_to_delete = model_obj.objects.exclude(id__in=pk_list)

            if self.allows_delete:
                for instance in instances_to_delete:
                    try:
                        instance.delete()
                    except IntegrityError:
                        return Response({
                            'row': 0,
                            'error_field_label': 'ID',
                            'error_field_value': '''
                                Cannot delete row because it is used as a reference by at least one other table.<br />
                                Affected ID:
                            ''' + str(instance.pk) + '''
                            <p>Please refresh the panel by clicking the refresh icon on the top rigth corner.</p>
                            '''
                        }, status=status.HTTP_400_BAD_REQUEST)
            elif instances_to_delete:
                return Response({
                    'row': 0,
                    'error_field_label': 'ID',
                    'error_field_value': '''This table does not allow deleting existing rows.'''
                }, status=status.HTTP_400_BAD_REQUEST)

            # Save valid datasets
            for s in serializer_save_list:
                s.save()

        except Exception as e:
            return Response({
                'row': 0,
                'error_field_label': 'Unknown',
                'error_field_value': '''An unexpected error occured. Please report this error to the administrator.
                <p><i>Error message: ''' + str(e) + '''</i></p>'''
            }, status=status.HTTP_400_BAD_REQUEST)

        # Return success message as JSON
        return Response(['Data saved successfully'], status=status.HTTP_200_OK)


class MasterTableHeaderAPIMixin(APIView, BaseAPIMixin, mixins_view.SecurityModelNameMixin):
    r"""
    View that loads the table header
    Assuming user group has required permissions.
    """

    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    target_model = Item
    permission_type = 'table'

    def get(self, request, format=None, **kwargs):
        # Get model name
        self.model_name = self.get_model_name(request.user)

        # Check if user has permissions
        if self.model_name == 401:
            content = {'message': '401 no access authorization'}
            return Response(content, status=status.HTTP_401_UNAUTHORIZED)

        # Define model
        model_obj = self.get_model_obj()

        # Return header field names
        model_fields = model_obj.get_form_field_names_verbose_list(model_obj)
        return JsonResponse(model_fields, safe=False)


# class TokenFieldAPIMixin(APIView, BaseAPIMixin, mixins_view.SecurityModelNameMixin):
#     r"""
#     View that loads the data for tokenfield. Get request only.
#     Assuming user group has required permissions.
#     """
#
#     user_permission_model = UserPermissions
#     group_permission_model = GroupPermissions
#     target_model = Item
#     permission_type = 'tokenfield'
#     model_name = None
#     serializer_name = None
#
#     def get(self, request, format=None, **kwargs):
#         # Get model name
#         self.model_name = self.get_model_name(request.user)
#
#         # Check if user has permissions
#         if self.model_name == 401:
#             content = {'message': '401 no access authorization'}
#             return Response(content, status=status.HTTP_401_UNAUTHORIZED)
#
#         # Exclude serializer from model_name
#         self.serializer_name = self.model_name
#         self.model_name = self.model_name.split('Serializer', 1)[0]
#
#         # Define model
#         model_obj = self.get_model_obj()
#
#         # Define serializer
#         serializer_obj = self.get_serializer_obj()
#
#         # Define queryset object
#         queryset = model_obj.objects.all()
#
#         # Return serialized data
#         serializer = serializer_obj(queryset, many=True)
#         return Response(serializer.data)


class StoredProcedureListMixin(views.TableProcedure, mixins_view.SecurityModelNameMixin):
    r"""
    View that shows the Console stored procedures that a user can run
    """

    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    target_model = Item
    permission_type = 'procedure'

    def get_context_dict(self, request):

        # Get procedure name list
        self.set_user(request.user)
        procedure_name_list = self.get_authorized_model_item_list()

        procedure_list = list()
        for procedure_name in procedure_name_list:
            item = Item.objects.get(permission_type='procedure', name=procedure_name)

            procedure_list.append({
                'number': item.sequence,
                'name': item.name,
                'label': item.label,
                'url': reverse_lazy('procedure_run', kwargs={'item': item.name}),
                'duration': item.duration,
                'completion_percentage': item.completion_percentage,
                'completion_dt': item.end_dt
            })

        procedure_list = sorted(procedure_list, key=lambda k: k['number'])

        return {
            'form_items': procedure_list,
            'message': {
                'text': 'No procedure available',
                'type': 'warning',
                'position_left': True
            }
        }


class StoredProcedureAPI(APIView, mixins_view.SecurityModelNameMixin):
    r"""
    View that runs a stored procedure provided as parameter
    """

    user_permission_model = UserPermissions
    group_permission_model = GroupPermissions
    target_model = Item
    permission_type = ['procedure', 'rpc']

    def get_model_obj(self, param):
        return None

    def get(self, request, format=None, **kwargs):

        # Check if procedure is currently running
        if not Item.objects.filter(
            permission_type__in=self.permission_type,
            start_dt__isnull=False,
            end_dt__isnull=True,
        ).exists():

            # Get model name
            procedure_name = self.get_model_name(request.user)

            # Get item object
            item = Item.objects.get(permission_type__in=self.permission_type, name=procedure_name)
            item_permission_type = item.permission_type

            # Update start_dt
            start_dt = timezone.now()
            item.start_dt = start_dt
            item.completion_percentage = 0
            item.save()

            # Check if user has permissions
            if procedure_name == 401:
                content = {'message': '401 no access authorization'}
                return Response(content, status=status.HTTP_401_UNAUTHORIZED)

            # If procedure is a database procedure
            if item_permission_type == 'procedure':

                # Run stored procedure (MySQL or MSSQL)
                try:
                    if 'mysql' in cp.DATABASE_ENGINE_DJANGO:
                        result = StoredProcedureModel.run_mysql(procedure_name)
                    else:
                        result = StoredProcedureModel.run_mssql(procedure_name)
                except (OperationalError) as e:
                    result = str(e)

                # Check if procedure returned error message
                if type(result) is str:
                    content = {'message': result}
                    item.start_dt = None
                    item.save()
                    return Response(content, status=status.HTTP_400_BAD_REQUEST)

            # If procedure is a RPC
            elif item_permission_type == 'rpc':
                result = self.get_model_obj(procedure_name)

            # Update end_dt
            end_dt = timezone.now()
            item.end_dt = end_dt
            item.completion_percentage = 100
            item.duration = int((end_dt-start_dt).total_seconds())
            item.save()

            # Get all items above current item
            next_items = Item.objects.filter(permission_type__in=self.permission_type, sequence__gt=item.sequence).update(completion_percentage=0)

        else:
            content = {'message': '409 procedure currently running by another user'}
            return Response(content, status=status.HTTP_409_CONFLICT)

        return Response(data={'message': result})
