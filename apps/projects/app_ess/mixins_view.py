from . import models

class SourcingFilter():

    def __init__(self):
        self.filter_dict = dict()
        # self.filter_dict['dim_pdas_id__exact'] = models.DimRelease.objects.all().last().id

        # dim_pdas_last = models.DimRelease.objects.all().last()
        # self.buying_program_id = dim_pdas_last.dim_buying_program_id
        # self.dim_pdas_dim_date_id = dim_pdas_last.dim_date.id
        # self.buying_program_name = models.DimBuyingProgram.objects.filter(pk=self.buying_program_id).first().name
