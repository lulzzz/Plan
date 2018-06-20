from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.BaseView.as_view(), name='base'),

    # Search
    url(r'^search_tab$', views.SearchResultsViewDefault.as_view(), name='search_tab'),
    url(r'^search_tab_one_product/(?P<pk>\d+)$', views.SearchResultsViewOneProduct.as_view(), name='search_tab_one_product'),
    url(r'^search_tab_multiple_product/(?P<keyword>.+)$', views.SearchResultsViewMultipleProduct.as_view(), name='search_tab_multiple_product'),
    url(r'^search_tab_one_store/(?P<pk>\d+)$', views.SearchResultsViewOneStore.as_view(), name='search_tab_one_store'),
    url(r'^search_tab_multiple_store/(?P<keyword>.+)$', views.SearchResultsViewMultipleStore.as_view(), name='search_tab_multiple_store'),

    # Master table
    url(r'^master_table_tab/(?P<item>[\w]+)$', views.MasterTableView.as_view(), name='master_table_tab'),

    # Dashboard
    url(r'^summary_tab$', views.SummaryView.as_view(), name='summary_tab'),

    # Strategic sales plan
    url(r'^strategic_sales_plan_tab$', views.StrategicSalesPlanView.as_view(), name='strategic_sales_plan_tab'),

    # Step 1: Store clustering
    url(r'^clustering_tab_store$', views.ClusteringViewStore.as_view(), name='clustering_tab_store'),
    url(r'^clustering_tab_assortment$', views.ClusteringViewAssortment.as_view(), name='clustering_tab_assortment'),

    # Step 2: Store clustering
    url(r'^sales_planning_tab_consensus$', views.SalesPlanningViewConsensus.as_view(), name='sales_planning_tab_consensus'),
    url(r'^sales_planning_tab_brand$', views.SalesPlanningViewBrand.as_view(), name='sales_planning_tab_brand'),
    url(r'^sales_planning_tab_retail$', views.SalesPlanningViewRetail.as_view(), name='sales_planning_tab_retail'),
    url(r'^sales_planning_tab_consolidated$', views.SalesPlanningViewConsolidated.as_view(), name='sales_planning_tab_consolidated'),

    # Step 3: Store clustering
    url(r'^range_planning_tab_architecture$', views.RangePlanningViewArchitecture.as_view(), name='range_planning_tab_architecture'),
    url(r'^range_planning_tab_master$', views.RangePlanningViewMaster.as_view(), name='range_planning_tab_master'),

    # Step 4: Store clustering
    url(r'^buy_planning_tab$', views.BuyPlanningView.as_view(), name='buy_planning_tab'),

    # Forecast
    url(r'^forecast_tab$', views.ForecastView.as_view(), name='forecast_tab'),

    # Simulations
    url(r'^clustering_simulation_tab$', views.ClusteringSimulationView.as_view(), name='clustering_simulation_tab'),

    # Profile
    url(r'^user_profile_tab$', views.ProfileView.as_view(), name='user_profile_tab'),
]
