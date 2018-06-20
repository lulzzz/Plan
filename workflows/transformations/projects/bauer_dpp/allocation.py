import datetime
from sqlalchemy.orm import aliased
from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine, and_
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, text
from sqlalchemy.ext.automap import automap_base

from workflows.core.database_utils import db_connect

# Create connection to database, TODO: these needs to be put somehwere else
engine = db_connect()
Session = sessionmaker(bind=engine)

Base = automap_base()
Base.prepare(engine, reflect=True)

dbo = Base.classes
session = Session()

sep = ' => '
allocations = list()
release = None
factory_ids = None
primary_factories = None
primary_locations = None
secondary_factories = None
secondary_locations = None
rqt_vendors = None
customer_names = None

def run():
    # Get data from database
    data = get_data()

    # Run allocation algorithm
    allocation_tree(data)

    # Save data to database
    session.commit()

def get_data():
    r"""
    Get target data from fact_demand_total joined with its corresponding tables.
    """
    # Define global variables
    global release

    # Get release item
    current_release_id = session.query(dbo.helper_pdas_footwear_vans_release_current).first().dim_release_id
    print('current_release_id', current_release_id)

    release = session.query(dbo.dim_release).filter(
        dbo.dim_release.id == current_release_id
    ).first()
    print("Retrieve release id Success")
    print('release_id', release.id)

    # Get business id
    businessid = session.query(dbo.dim_business).filter(
        dbo.dim_business.brand == 'Vans',
        dbo.dim_business.product_line == 'Footwear'
    ).first().id

    # Factory Placeholder
    dim_factory_id_placeholder = session.query(dbo.dim_factory).filter(
        dbo.dim_factory.is_placeholder == 1,
        dbo.dim_factory.placeholder_level == 'PLACEHOLDER'
    ).first().id

    # Release month dim_date_id
    pdas_full_date = session.query(dbo.dim_date).filter(
        dbo.dim_date.id == release.dim_date_id
    ).first().full_date

    pdas_release_month_date_id = session.query(dbo.dim_date).filter(
        dbo.dim_date.full_date == datetime.date(pdas_full_date.year, pdas_full_date.month, 1)
    ).first().id
    print('pdas_release_month_date_id', pdas_release_month_date_id)

    # Release full dim_date_id
    pdas_release_full_date_id = release.dim_date_id

    # Dim buying program id
    dim_buying_program_id = release.dim_buying_program_id
    print('dim_buying_program_id', dim_buying_program_id)

    fact_location = aliased(dbo.dim_location)
    cust_location = aliased(dbo.dim_location)

    # Query items to allocate
    query = session.query(
        dbo.fact_demand_total,
        dbo.dim_buying_program,
        dbo.dim_demand_category,
        dbo.dim_product,
        dbo.dim_construction_type,
        dbo.dim_factory,
        fact_location,
        dbo.dim_customer,
        cust_location
    )
    data = query.filter(
        dbo.fact_demand_total.dim_buying_program_id == dbo.dim_buying_program.id,
        dbo.fact_demand_total.dim_demand_category_id == dbo.dim_demand_category.id,
        dbo.fact_demand_total.dim_product_id == dbo.dim_product.id,
        dbo.dim_product.dim_construction_type_id == dbo.dim_construction_type.id,
        dbo.fact_demand_total.dim_factory_id_original_unconstrained == dbo.dim_factory.id,
        dbo.dim_factory.dim_location_id == fact_location.id,
        dbo.fact_demand_total.dim_customer_id == dbo.dim_customer.id,
        dbo.dim_customer.dim_location_id == cust_location.id,

        dbo.fact_demand_total.dim_release_id == release.id,
        dbo.fact_demand_total.dim_business_id == businessid,
        dbo.fact_demand_total.dim_date_id >= pdas_release_month_date_id,
        dbo.fact_demand_total.dim_buying_program_id == dim_buying_program_id,
        # dbo.fact_demand_total.edit_dt.is_(None),
        dbo.dim_demand_category.name.in_(['Forecast', 'Need to Buy']),
    ).all()

    return data

def allocation_tree(data):

    # Define global variables
    global release
    global sep
    global allocations
    global factory_ids
    global primary_factories
    global primary_locations
    global secondary_factories
    global secondary_locations
    global rqt_vendors
    global customer_names

    # == Data query: helper tables =======================
    # Get all full dates
    full_dates = {f.id:f.full_date for f in session.query(dbo.dim_date)}

    # Get helper factory quick turn table
    factory_quick_turn = {f.material_id:f.factory_short_name for f in session.query(dbo.helper_pdas_footwear_vans_fty_qt)}

    # Get factory IDs mapped with factory short name
    factory_ids = {f.short_name: f.id for f in session.query(dbo.dim_factory)}

    # Get priority list primary factory names
    query = session.query(dbo.fact_priority_list, dbo.dim_factory, dbo.dim_location, dbo.dim_product)
    items = query.filter(
        dbo.fact_priority_list.dim_factory_id_1 == dbo.dim_factory.id,
        dbo.dim_factory.dim_location_id == dbo.dim_location.id,
        dbo.fact_priority_list.dim_release_id == release.id,
        dbo.fact_priority_list.dim_product_id == dbo.dim_product.id
    ).all()
    primary_factories = {dp.material_id: f.short_name for fp, f, _, dp in items}
    primary_locations = {dp.material_id: l.country_code_a2 for fp, _, l, dp in items}

    # Get priority list secondary factory names
    query = session.query(dbo.fact_priority_list, dbo.dim_factory, dbo.dim_location, dbo.dim_product)
    items = query.filter(
        dbo.fact_priority_list.dim_factory_id_2 == dbo.dim_factory.id,
        dbo.dim_factory.dim_location_id == dbo.dim_location.id,
        dbo.fact_priority_list.dim_release_id == release.id,
        dbo.fact_priority_list.dim_product_id == dbo.dim_product.id
    ).all()
    secondary_factories = {dp.material_id: f.short_name for fp, f, _, dp in items}
    secondary_locations = {dp.material_id: l.country_code_a2 for fp, _, l, dp in items}

    # Get customer names
    customer_names = {c.id: c.name for c in session.query(dbo.dim_customer)}

    # Get RQT table
    rqt_vendors = {(f.material_id, f.region, f.sold_to_party): f.factory_short_name
                   for f in session.query(dbo.helper_pdas_footwear_vans_retail_qt)}
    del items


    print('start allocation tree')
    # == Allocation Tree =======================
    print(data[:10])
    for demand, buying_program, demand_category, product, construction_type, factory, factory_loc, customer, customer_loc in data:
        allocation_logic = ''

        date_buy = full_dates[demand.dim_date_id]
        date_crd = full_dates[release.dim_date_id]

        factory_quick_turn_vendor = factory_quick_turn.get(product.material_id)

        # Sold to party to use:
        if demand_category.name == 'Forecast':
            sold_to_party = demand.sold_to_customer_name
        else:
            sold_to_party = customer.sold_to_party

        print('buying program', buying_program.name)
        print('sold_to_category', customer.sold_to_category)
        if customer.sold_to_category == 'DC':

            allocation_logic += sep + 'Sold to category: ' + customer.sold_to_category
            if buying_program.name == 'Bulk Buy' or demand_category.name == 'Forecast':

                allocation_logic += sep + 'Buying program: ' + buying_program.name
                if customer_loc.region == 'EMEA':
                    allocation_logic += sep + 'Region: ' + customer_loc.region
                    sub01(demand, allocation_logic, product)

                elif customer_loc.region in ('NORA', 'CASA'):
                    allocation_logic += sep + 'Region: ' + customer_loc.region
                    if sold_to_party.lower().find('can') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub02(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('us') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub05(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('brazil') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub08(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('chile') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub09(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('mx') > -1 or sold_to_party.lower().find('mex') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

                elif customer_loc.region == 'APAC':
                    allocation_logic += sep + 'Region: ' + customer_loc.region
                    if sold_to_party.lower().find('china') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub07(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('korea') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub06(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('india') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub06(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('my') > -1 or sold_to_party.lower().find('malaysia') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('singapore') > -1 or sold_to_party.lower().find('sg') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('hong kong') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

            elif buying_program.name in ('Retail Quick Turn', 'Retail Quick Turn Built To Forecast'):
                allocation_logic += sep + 'Buying program: ' + buying_program.name
                print('RQT')
                sub_rqt(demand, allocation_logic, product, customer, customer_loc)

            elif buying_program.name == 'Ad-Hoc Out of Sync':
                allocation_logic += sep + 'Buying program: ' + buying_program.name
                allocation_logic += sep + 'Lead time: ' + str((date_buy - date_crd).days)

                if (date_buy - date_crd >= datetime.timedelta(73)) or (date_buy - date_crd < datetime.timedelta(73) and factory_quick_turn_vendor is None):

                    if customer_loc.region == 'EMEA':
                        allocation_logic += sep + 'Region: ' + customer_loc.region
                        sub01(demand, allocation_logic, product)

                    elif customer_loc.region in ('NORA', 'CASA'):
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.lower().find('can') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub02(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('us') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub05(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('brazil') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub08(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('chile') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub09(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('mx') > -1 or sold_to_party.lower().find('mex') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                    elif customer_loc.region == 'APAC':
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.lower().find('china') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub07(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('korea') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub06(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('india') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub06(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('my') > -1 or sold_to_party.lower().find('malaysia') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('singapore') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('hong kong') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                else:
                    dim_factory_id_original_unconstrained = factory_ids[factory_quick_turn_vendor]
                    allocation_logic += sep + 'VQT Vendor'
                    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

            elif buying_program.name == 'Scheduled Out of Sync':
                allocation_logic += sep + 'Buying program: ' + buying_program.name
                allocation_logic += sep + 'Lead time: ' + str((date_buy - date_crd).days)

                if (date_buy - date_crd >= datetime.timedelta(73)) or (date_buy - date_crd < datetime.timedelta(73) and factory_quick_turn_vendor is None):

                    if customer_loc.region == 'EMEA':
                        allocation_logic += sep + 'Region: ' + customer_loc.region
                        sub01(demand, allocation_logic, product)

                    elif customer_loc.region in ('NORA', 'CASA'):
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.lower().find('can') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub02(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('us') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub05(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('brazil') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub08(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('chile') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub09(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('mx') > -1 or sold_to_party.lower().find('mex') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                    if customer_loc.region == 'APAC':
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.lower().find('china') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub07(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('korea') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub06(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('india') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub06(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('my') > -1 or sold_to_party.lower().find('malaysia') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('singapore') > -1 or sold_to_party.lower().find('sg') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('hong kong') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                else:
                    dim_factory_id_original_unconstrained = factory_ids[factory_quick_turn_vendor]
                    allocation_logic += sep + 'VQT Vendor'
                    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

        elif customer.sold_to_category == 'Direct+International':
            allocation_logic += sep + 'Sold to category: ' + customer.sold_to_category

            if buying_program.name == 'Bulk Buy' or demand_category.name == 'Forecast':
                allocation_logic += sep + 'Buying program: ' + buying_program.name

                if customer_loc.region == 'EMEA':
                    allocation_logic += sep + 'Region: ' + customer_loc.region
                    sub10(demand, allocation_logic, product)

                elif customer_loc.region in ('NORA', 'CASA'):
                    allocation_logic += sep + 'Region: ' + customer_loc.region

                    if sold_to_party.find('Canada') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub02(demand, allocation_logic, product)

                    elif sold_to_party.lower().find('us') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub04(demand, allocation_logic, product, customer)

                    elif sold_to_party.find('Mexico') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

                    elif sold_to_party.find('International') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

                elif customer_loc.region == 'APAC':
                    allocation_logic += sep + 'Region: ' + customer_loc.region

                    if sold_to_party.lower().find('korea') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub06(demand, allocation_logic, product)

                    elif sold_to_party.find('APAC Direct') > -1:
                        allocation_logic += sep + 'Sold to party: ' + sold_to_party
                        sub10(demand, allocation_logic, product)

            elif buying_program.name in ('Retail Quick Turn', 'Retail Quick Turn Built To Forecast'):
                allocation_logic += sep + 'Buying program: ' + buying_program.name
                print('RQT2')
                sub_rqt(demand, allocation_logic, product, customer, customer_loc)

            elif buying_program.name == 'Ad Hoc Vor Quick Turn':
                allocation_logic += sep + 'Buying program: ' + buying_program.name
                allocation_logic += sep + 'Lead time: ' + str((date_buy - date_crd).days)

                if (date_buy - date_crd >= datetime.timedelta(73)) or (date_buy - date_crd < datetime.timedelta(73) and factory_quick_turn_vendor is None):

                    if customer_loc.region == 'EMEA':
                        allocation_logic += sep + 'Region: ' + customer_loc.region
                        sub01(demand, allocation_logic, product)

                    elif customer_loc.region in ('NORA', 'CASA'):
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.find('Canada') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub02(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('us') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub04(demand, allocation_logic, product, customer)

                        elif sold_to_party.find('Mexico') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                    elif customer_loc.region == 'APAC':
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.lower().find('korea') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub06(demand, allocation_logic, product)

                        elif sold_to_party.find('APAC Direct') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                else:
                    dim_factory_id_original_unconstrained = factory_ids[factory_quick_turn_vendor]
                    allocation_logic += sep + 'VQT Vendor'
                    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

            elif buying_program.name == 'Scheduled Out of Sync':
                allocation_logic += sep + 'Buying program: ' + buying_program.name
                allocation_logic += sep + 'Lead time: ' + str((date_buy - date_crd).days)

                if (date_buy - date_crd >= datetime.timedelta(73)) or (date_buy - date_crd < datetime.timedelta(73) and factory_quick_turn_vendor is None):

                    if customer_loc.region == 'EMEA':
                        allocation_logic += sep + 'Region: ' + customer_loc.region
                        sub01(demand, allocation_logic, product)

                    elif customer_loc.region in ('NORA', 'CASA'):
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.find('Canada') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub02(demand, allocation_logic, product)

                        elif sold_to_party.lower().find('us') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub04(demand, allocation_logic, product, customer)

                        elif sold_to_party.find('Mexico') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                    elif customer_loc.region == 'APAC':
                        allocation_logic += sep + 'Region: ' + customer_loc.region

                        if sold_to_party.lower().find('korea') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub06(demand, allocation_logic, product)

                        elif sold_to_party.find('APAC Direct') > -1:
                            allocation_logic += sep + 'Sold to party: ' + sold_to_party
                            sub10(demand, allocation_logic, product)

                else:
                    dim_factory_id_original_unconstrained = factory_ids[factory_quick_turn_vendor]
                    allocation_logic += sep + 'VQT Vendor'
                    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

        elif customer.sold_to_category == 'Crossdock':
            allocation_logic += sep + 'Sold to category: ' + customer.sold_to_category

            if buying_program.name == 'Bulk Buy' or demand_category.name == 'Forecast':
                allocation_logic += sep + 'Buying program: ' + buying_program.name

                if customer_loc.region == 'EMEA':
                    allocation_logic += sep + 'Region: ' + customer_loc.region
                    sub01(demand, allocation_logic, product)

        else:
            allocation_logic = ' => Sold to category: ' + customer.sold_to_category + ' => Buying program: ' + buying_program.name + ' => Region: ' + customer_loc.region + ' => Sold to party: ' + sold_to_party
            updater(demand, allocation_logic)

def updater(demand, allocation_logic, dim_factory_id_original_unconstrained=None, component_factory_short_name=None):

    # Update allocation logic
    demand.allocation_logic_unconstrained = allocation_logic

    # Update factory allocation
    if dim_factory_id_original_unconstrained is not None:
        demand.dim_factory_id_original_unconstrained = dim_factory_id_original_unconstrained
        demand.dim_factory_id_original_constrained = dim_factory_id_original_unconstrained
        demand.dim_factory_id = dim_factory_id_original_unconstrained
        demand.component_factory_short_name = component_factory_short_name

def sub01(demand, allocation_logic, product):
    # Debug
    allocations.append(1)

    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_factory_name_priority_list_secondary = secondary_factories.get(product.material_id)
    dim_location_country_code_a2 = primary_locations.get(product.material_id)
    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0
    dim_product_dtp_mtl = product.dtp_mtl if not product.clk_mtl is None else 0
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    fact_priority_list_source_count = 0
    if dim_factory_name_priority_list_primary:
        fact_priority_list_source_count += 1
    if dim_factory_name_priority_list_secondary:
        fact_priority_list_source_count += 1

    # Sub decision tree logic

    # CLK MTL?
    if dim_product_clk_mtl == 1:
        dim_factory_id_original_unconstrained = factory_ids.get('CLK')
        allocation_logic += sep + 'CLK MTL'

    # DTP MTL?
    elif dim_product_dtp_mtl == 1:
        dim_factory_id_original_unconstrained = factory_ids.get('DTP')
        allocation_logic += sep + 'DTP MTL'

    # Flex?
    elif product.style_complexity.find('Flex') > -1:
        dim_factory_id_original_unconstrained = factory_ids.get('SJV')
        allocation_logic += sep + 'Flex'

    # Single Source?
    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Single Source' + sep +'1st priority'

    # 1st priority = COO China?
    elif dim_location_country_code_a2 == 'CN':
        allocation_logic += sep + '1st priority = COO China' + sep +'2nd priority'
        if dim_factory_name_priority_list_secondary is not None:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)
            allocation_logic += sep + dim_factory_name_priority_list_secondary

        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + 'not found'+ sep +'1st priority'

            if dim_factory_name_priority_list_primary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_primary
    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '1st priority = COO not China'+ sep +'1st priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    # Update entry
    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub02(demand, allocation_logic, product):
    # Debug
    allocations.append(2)

    # Variables assignments
    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0

    # Sub decision tree logic

    # CLK MTL?
    if dim_product_clk_mtl == 1:

        dim_factory_id_original_unconstrained = factory_ids.get('CLK')
        allocation_logic += sep + 'CLK MTL'

    # First priority
    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Not CLK MTL' + sep + '1st priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub03(demand, allocation_logic, product):
    # Debug
    allocations.append(3)

    # Variable assignments

    dim_factory_id_original_unconstrained = None
    fact_priority_list_source_count = 0

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_factory_name_priority_list_secondary = secondary_factories.get(product.material_id)

    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0
    dim_product_dtp_mtl = product.dtp_mtl if not product.clk_mtl is None else 0
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    if dim_factory_name_priority_list_primary:
        fact_priority_list_source_count += 1
    if dim_factory_name_priority_list_secondary:
        fact_priority_list_source_count += 1

    dim_location_country_code_a2 = primary_locations.get(product.material_id)

    # Sub decision tree logic

    # CLK MTL?
    if dim_product_clk_mtl == 1:
        dim_factory_id_original_unconstrained = factory_ids.get('CLK')
        allocation_logic += sep + 'CLK MTL'

    # Flex?
    elif product.style_complexity.find('Flex') > -1:
        dim_factory_id_original_unconstrained = factory_ids.get('SJV')
        allocation_logic += sep + 'Flex'

    # Single Source?
    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Single Source'

    # 1st priority = COO China?
    elif dim_location_country_code_a2 == 'CN':
        allocation_logic += sep + '1st priority = COO China' + sep + '2nd priority'

        if dim_factory_name_priority_list_secondary is not None:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)
            allocation_logic += sep + dim_factory_name_priority_list_secondary

        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + 'not found' + sep + '1st priority'
            if dim_factory_name_priority_list_primary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_primary

    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '1st priority = COO not China' + sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub04(demand, allocation_logic, product, customer):
    # Debug
    allocations.append(4)

    dim_factory_id_original_unconstrained = None

    # Variable assignments

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    # Sub decision tree logic

    # SJD MTL and customer is Zumiez or Kohls or Journeys?
    if dim_product_sjd_mtl == 1 and (customer.name.lower().find('zumiez') > -1
                                    or customer.name.find('kohls') > -1
                                    or customer.name.lower().find('journeys') > -1):
        dim_factory_id_original_unconstrained = factory_ids.get('SJD')
        allocation_logic += sep + 'SJD MTL'

    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub05(demand, allocation_logic, product):
    # Debug
    allocations.append(5)

    # Variable assignments
    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    # Sub decision tree logic

    # SJD MTL?
    if dim_product_sjd_mtl == 1:
        dim_factory_id_original_unconstrained = factory_ids.get('SJD')
        allocation_logic += sep + 'SJD MTL'

    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub06(demand, allocation_logic, product):
    # Debug
    allocations.append(6)

    # Variable assignments

    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_factory_name_priority_list_secondary = secondary_factories.get(product.material_id)

    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0
    dim_product_dtp_mtl = product.dtp_mtl if not product.clk_mtl is None else 0
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    fact_priority_list_source_count = 0
    if dim_factory_name_priority_list_primary:
        fact_priority_list_source_count += 1
    if dim_factory_name_priority_list_secondary:
        fact_priority_list_source_count += 1

    dim_location_country_code_a2_primary = primary_locations.get(product.material_id)
    dim_location_country_code_a2_secondary = secondary_locations.get(product.material_id)

    # Sub decision tree logic

    # Flex?
    if product.style_complexity.find('Flex') > -1:
        dim_factory_id_original_unconstrained = factory_ids.get('SJV')
        allocation_logic += sep + 'Flex'

    # CLK MTL?
    elif dim_product_clk_mtl == 1:
        dim_factory_id_original_unconstrained = factory_ids.get('CLK')
        allocation_logic += sep + 'CLK MTL'

    # DTP MTL?
    elif dim_product_dtp_mtl == 1:
        dim_factory_id_original_unconstrained = factory_ids.get('DTP')
        allocation_logic += sep + 'DTP MTL'

    # Single Source?
    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Single Source'

    # 1st priority = COO China?
    elif dim_location_country_code_a2_primary != 'CN':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '1st priority = COO not China' + sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    # 2nd priority = COO China?
    elif dim_location_country_code_a2_secondary == 'CN':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '2nd priority = COO China' + sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    else:
        allocation_logic += sep + '2nd priority = COO not China' + sep + '2nd priority'
        if dim_factory_name_priority_list_secondary is not None:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)
            allocation_logic += sep + dim_factory_name_priority_list_secondary

        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + 'not found' + sep + '1st priority'

            if dim_factory_name_priority_list_primary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub07(demand, allocation_logic, product):
    # Debug
    allocations.append(7)

    # Variable assignments
    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_factory_name_priority_list_secondary = secondary_factories.get(product.material_id)

    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0
    dim_product_dtp_mtl = product.dtp_mtl if not product.clk_mtl is None else 0
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    fact_priority_list_source_count = 0
    if dim_factory_name_priority_list_primary:
        fact_priority_list_source_count += 1
    if dim_factory_name_priority_list_secondary:
        fact_priority_list_source_count += 1

    dim_location_country_code_a2 = primary_locations.get(product.material_id)

    # Sub decision tree logic

    # Flex?
    if product.style_complexity.find('Flex') > -1 and dim_factory_name_priority_list_primary == 'ICC':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Flex'

    elif product.style_complexity.find('Flex') > -1 and dim_factory_name_priority_list_primary == 'DTC':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Flex'

    elif product.style_complexity.find('Flex') > -1 and dim_factory_name_priority_list_primary == 'SJV':
        dim_factory_id_original_unconstrained = factory_ids.get('HSC')
        allocation_logic += sep + 'Flex'

    # Single Source?
    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1 and dim_factory_name_priority_list_primary == 'ICC':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Single Source'

    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1 and dim_factory_name_priority_list_primary == 'DTC':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Single Source'

    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1 and dim_factory_name_priority_list_primary == 'SJV':
        dim_factory_id_original_unconstrained = factory_ids.get('HSC')
        allocation_logic += sep + 'Single Source'

    # 1st priority = COO China?
    elif dim_location_country_code_a2 == 'CN':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '1st priority = COO China' + sep + '1st priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    # 1st priority = SJV?
    elif dim_factory_name_priority_list_primary == 'SJV':
        dim_factory_id_original_unconstrained = factory_ids.get('HSC')
        allocation_logic += sep + '1st priority = SJV' + sep + '1st priority'

        if dim_factory_name_priority_list_secondary is not None:
            allocation_logic += sep + 'HSC'

    else:
        # 2nd priority != 0
        allocation_logic += sep + '1st priority = not SJV' + sep + '2nd priority'

        if dim_factory_name_priority_list_secondary is not None:
            # SJV => HSC
            if dim_factory_name_priority_list_secondary == 'SJV':
                dim_factory_id_original_unconstrained = factory_ids.get('HSC')
                allocation_logic += sep + dim_factory_name_priority_list_secondary

            # Others => Others
            else:
                dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)
                allocation_logic += sep + dim_factory_name_priority_list_secondary

        # 2nd priority = 0
        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + 'not found' + sep + '1st priority'
            if dim_factory_name_priority_list_primary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_primary


    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub08(demand, allocation_logic, product):
    # Debug
    allocations.append(8)

    # Variable assignments
    dim_factory_id_original_unconstrained = None
    component_factory_short_name = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_factory_name_priority_list_secondary = secondary_factories.get(product.material_id)

    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0
    dim_product_dtp_mtl = product.dtp_mtl if not product.clk_mtl is None else 0
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    dim_location_country_code_a2_primary = primary_locations.get(product.material_id)
    dim_location_country_code_a2_secondary = secondary_locations.get(product.material_id)

    fact_priority_list_source_count = 0
    if dim_factory_name_priority_list_primary:
        fact_priority_list_source_count += 1
    if dim_factory_name_priority_list_secondary:
        fact_priority_list_source_count += 1


    # Sub decision tree logic
    # Flex?
    if product.style_complexity.find('Flex') > -1:
        dim_factory_id_original_unconstrained = factory_ids.get('SJV')
        component_factory_short_name = 'SJV'
        allocation_logic += sep + 'Flex' + sep + 'SJV'

    # Single Source?
    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1:
        allocation_logic += sep + 'Single Source'

        # 1st priority = DTC?
        if dim_factory_name_priority_list_primary == 'DTC':
            dim_factory_id_original_unconstrained = factory_ids.get('DTP')
            component_factory_short_name = 'DTC'
            allocation_logic += sep + '1st priority = DTC' + sep + 'DTP'

        # 1st priority = COO China?
        elif dim_location_country_code_a2_primary == 'CN':
            dim_factory_id_original_unconstrained = factory_ids.get('SJV')
            allocation_logic += sep + '1st priority = COO not China' + sep + 'SJV'
            if dim_factory_name_priority_list_primary is not None:
                component_factory_short_name = dim_factory_name_priority_list_primary

            else:
                allocation_logic += sep + '1st priority not found'
                component_factory_short_name = '1st priority not found'

        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + '1st priority = COO China'

            if dim_factory_name_priority_list_primary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_primary
                component_factory_short_name = dim_factory_name_priority_list_primary

    # 2nd Priority = COO China?
    elif dim_location_country_code_a2_secondary == 'CN':
        dim_factory_id_original_unconstrained = factory_ids.get('SJV')
        allocation_logic += sep + '2nd priority = COO China' + sep + 'SJV'

        if dim_factory_name_priority_list_primary is not None:
            component_factory_short_name = dim_factory_name_priority_list_primary

        else:
            component_factory_short_name = '1st priority not found'

    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)
        allocation_logic += sep + '2nd priority = COO not China'

        if dim_factory_name_priority_list_secondary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_secondary
            component_factory_short_name = dim_factory_name_priority_list_secondary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained, component_factory_short_name)

def sub09(demand, allocation_logic, product):
    # Debug
    allocations.append(9)

    # Variable assignments
    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)
    dim_factory_name_priority_list_secondary = secondary_factories.get(product.material_id)

    dim_product_clk_mtl = product.clk_mtl if not product.clk_mtl is None else 0
    dim_product_dtp_mtl = product.dtp_mtl if not product.clk_mtl is None else 0
    dim_product_sjd_mtl = product.sjd_mtl if not product.clk_mtl is None else 0

    fact_priority_list_source_count = 0
    if dim_factory_name_priority_list_primary:
        fact_priority_list_source_count += 1
    if dim_factory_name_priority_list_secondary:
        fact_priority_list_source_count += 1

    dim_location_country_code_a2_primary = primary_locations.get(product.material_id)
    dim_location_country_code_a2_secondary = secondary_locations.get(product.material_id)

    # Sub decision tree logic

    # Flex?
    if product.style_complexity.find('Flex') > -1 and dim_factory_name_priority_list_primary == 'ICC':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Flex'

    elif product.style_complexity.find('Flex') > -1 and dim_factory_name_priority_list_primary == 'DTC':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + 'Flex'

    elif product.style_complexity.find('Flex') > -1 and dim_factory_name_priority_list_primary == 'SJV':
        dim_factory_id_original_unconstrained = factory_ids.get('HSC')
        allocation_logic += sep + 'Flex'

    # Single Source?
    elif fact_priority_list_source_count == 1 and (dim_product_clk_mtl + dim_product_dtp_mtl + dim_product_sjd_mtl) <= 1:
        allocation_logic += sep + 'Single Source'

        if dim_factory_name_priority_list_primary == 'SJV':
            dim_factory_id_original_unconstrained = factory_ids.get('HSC')
            allocation_logic += sep + '1st priority = SJV' + sep + 'HSC'

        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + '1st priority = not SJV' + sep + '1st priority'

    # Second priority null?
    elif dim_factory_name_priority_list_secondary is None:
        allocation_logic += sep + '2nd priority = 0'

        if dim_factory_name_priority_list_primary == 'SJV':
            dim_factory_id_original_unconstrained = factory_ids.get('HSC')
            allocation_logic += sep + '1st priority = SJV' + sep + 'HSC'

        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
            allocation_logic += sep + '1st priority = not SJV' + sep + '1st priority'

    # 1st priority = COO China?
    elif dim_location_country_code_a2_primary == 'CN':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '1st priority = COO China' + sep + '1st priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    # 2nd priority = COO China?
    elif dim_location_country_code_a2_secondary == 'CN':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)
        allocation_logic += sep + '2nd priority = COO China' + sep + 'Second priority'

        if dim_factory_name_priority_list_secondary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_secondary

    # 1st priority = COO Vietnam?
    elif dim_location_country_code_a2_primary == 'VN':
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '1st priority = COO Vietnam' + sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    # 2nd priority = COO Vietnam?
    elif dim_location_country_code_a2_secondary == 'VN':
        allocation_logic += sep + '2nd priority = COO Vietnam' + sep + 'Second priority'

        # SJV => HSC
        if dim_factory_name_priority_list_secondary == 'SJV':
            dim_factory_id_original_unconstrained = factory_ids.get('HSC')

            if dim_factory_name_priority_list_secondary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_secondary

        # Others => Others
        else:
            dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_secondary)

            if dim_factory_name_priority_list_secondary is not None:
                allocation_logic += sep + dim_factory_name_priority_list_secondary

    else:
        dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
        allocation_logic += sep + '2nd priority = COO not Vietnam' + sep + 'First priority'

        if dim_factory_name_priority_list_primary is not None:
            allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub10(demand, allocation_logic, product):
    # Debug
    allocations.append(10)

    # Variable assignments
    dim_factory_id_original_unconstrained = None

    dim_factory_name_priority_list_primary = primary_factories.get(product.material_id)

    # Sub decision tree logic

    dim_factory_id_original_unconstrained = factory_ids.get(dim_factory_name_priority_list_primary)
    allocation_logic += sep + 'First priority'

    if dim_factory_name_priority_list_primary is not None:
        allocation_logic += sep + dim_factory_name_priority_list_primary

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)

def sub_rqt(demand, allocation_logic, product, customer, customer_loc):
    # Debug
    allocations.append('rqt')

    dim_factory_id_original_unconstrained = None

    # Variable assignments
    rqt_vendor =  rqt_vendors.get((product.material_id, customer_loc.region, customer.sold_to_party), 'PLACEHOLDER')

    # Sub decision tree logic
    dim_factory_id_original_unconstrained = factory_ids.get(rqt_vendor)

    if dim_factory_id_original_unconstrained is not None:
        allocation_logic += sep + rqt_vendor + ' RQT MTL'

    if dim_factory_id_original_unconstrained is None:
        allocation_logic += sep + 'Not found'

    updater(demand, allocation_logic, dim_factory_id_original_unconstrained)
