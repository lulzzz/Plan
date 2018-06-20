import json
import sys
import os
import time
import pandas as pd
import numpy as np
import datetime
from tqdm import tqdm
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Float, Date, Boolean, Column, Integer, String, DateTime, ForeignKey
import sqlalchemy
from sqlalchemy import and_, func
import collections

from django.conf import settings as cp

from . import Session_target, Session_source, engine_target, engine_source


def upsert_dim_product(productattributetypeid_dict):
    r"""
    Update insert dim_product
    """

    start_time = time.time()
    print('Task - Load table dim_product')

    # We define table classes ourselves because they don't have any primary key and automap_base won't work
    Base = declarative_base()

    class Product(Base):
        __tablename__ = "Product"

        ProductID = Column(Integer, primary_key=True)
        ProductCode = Column(String)
        SupplierProductCode = Column(String)
        InternalProductCode = Column(String)
        GTIN = Column(String)
        ProductShortDescription = Column(String)
        ProductDescription = Column(String)
        ProductDisplayLabel = Column(String)
        StandardCostPrice = Column(Float)
        StandardSellingPrice = Column(Float)
        PackSize = Column(Integer)
        ImageName1 = Column(String)
        ImageName2 = Column(String)
        ImageName3 = Column(String)
        SortOrder = Column(Integer)
        StartDate = Column(Date)
        EndDate = Column(Date)
        UIActive = Column(Boolean)
        Locked = Column(Boolean)
        Locked_By = Column(String)
        InsertDate = Column(DateTime)
        UpdateDate = Column(DateTime)
        InsertSource = Column(String)
        UpdateSource = Column(String)
        FAS_Groups = Column(String)

    class Product_Attribute_Relation(Base):
        __tablename__ = 'Product_Attribute_Relation'

        ProductAttributeTypeID = Column(Integer)
        ProductCode = Column(String)
        ProductAttributeCode = Column(String)
        ProductID = Column(Integer, primary_key=True)
        ProductAttributeID = Column(Integer, primary_key=True)

    class Product_Attributes(Base):
        __tablename__ = 'Product_Attributes'

        ProductAttributeID = Column(Integer, primary_key=True)
        ProductAttributeTypeID = Column(Integer)
        ProductAttributeCode = Column(String)
        ProductAttributeShortDescription = Column(String)
        ProductAttributeDescription = Column(String)
        ProductAttributeDisplayLabel = Column(String)
        SortOrder = Column(Integer)
        UIActive = Column(Boolean)
        InsertDate = Column(DateTime)
        UpdateDate = Column(DateTime)

    s_session = Session_source()

    t = automap_base()
    t.prepare(engine_target, reflect=True)
    t_session = Session_target()

    # Query items from source product
    source_products = s_session.query(
        Product, Product_Attribute_Relation, Product_Attributes
    ).filter(
        Product.ProductID == Product_Attribute_Relation.ProductID,
        Product_Attributes.ProductAttributeID == Product_Attribute_Relation.ProductAttributeID,
    ).all()

    # mapping between source field names and target field names
    target_fields = {
        'Colour': 'colour',
        'Size': 'size',
        'Style': 'style',
        'Category': 'category',
        'Division': 'division',
        'Essential Trend': 'essential_trend',
        'Basic Fashion Colour': 'basic_fashion',
        'Quality': 'quality',
    }

    # mapping between PorductAttributeTypeID and target field names
    fields = {int(v):target_fields.get(k) for k,v in productattributetypeid_dict.items() if k in target_fields}

    # Build product fields values
    source_values = collections.defaultdict(dict)
    for product, _, attribute in source_products:

        # add product metadata
        if source_values.get(product.ProductID) is None:
            source_values[product.ProductID]['id'] = product.ProductID
            source_values[product.ProductID]['productcode'] = product.ProductCode
            source_values[product.ProductID]['productshortdescription'] = product.ProductShortDescription
            source_values[product.ProductID]['productdescription'] = product.ProductDescription
            source_values[product.ProductID]['image'] = product.ImageName1

        # add attributes for the given productID
        if attribute.ProductAttributeTypeID in fields:
            source_values[product.ProductID][fields[attribute.ProductAttributeTypeID]] = attribute.ProductAttributeDisplayLabel

    # Save product values into target database
    for values in source_values.values():
        t_session.merge(
            t.classes.app_dms_dimproduct(**values)
        )

    print('Task completed successfully')
    print('Task duration: {} seconds, Processed: {} entries'.format(
        int((time.time() - start_time)), len(source_values)
    ))


def upsert_dim_store():
    r"""
    Generate dim_store based on store (DMS load) and store_sales (IAP user input)
    """

    start_time = time.time()
    print('Task - Load table dim_store')

    Base = declarative_base()

    class Store(Base):
        __tablename__ = 'Store'

        StoreID = Column(Integer, primary_key=True)
        StoreCode = Column(String)
        StoreName = Column(String)
        StoreDisplayLabel = Column(String)
        ILN = Column(String)
        City = Column(String)
        RegionTaxRate = Column(Integer)
        LocalCurrency = Column(String)

    # DMS
    session_source = Session_source()

    Base_target = automap_base()
    Base_target.prepare(engine_target, reflect=True)
    session_target = Session_target()

    # get placeholders id
    dim_channel_placeholder_id = 1
    dim_location_placeholder_id = session_target.query(
        Base_target.classes.app_dms_dimlocation
    ).filter(
        Base_target.classes.app_dms_dimlocation.country == 'AUSTRIA'
    ).first().id

    # Query source and target
    source_stores = session_source.query(Store).all()
    dim_store_target = session_target.query(Base_target.classes.app_dms_dimstore).all()
    dim_store_target_id = {s.id:s for s in dim_store_target}

    # Transfer data
    count_updated = 0
    new_stores = list()
    for source_store in source_stores:
        store_target = dim_store_target_id.get(source_store.StoreID)
        if store_target is not None:
            # if existing in DB we update with found source data
            count_updated += 1
            store_target.id = source_store.StoreID
            store_target.store_code = source_store.StoreCode
            store_target.store_name = source_store.StoreName
            store_target.store_display_label = source_store.StoreDisplayLabel
            store_target.iln = source_store.ILN
            store_target.city = source_store.City
            store_target.region_tax_rate = source_store.RegionTaxRate
            store_target.local_currency = source_store.LocalCurrency
        else:
            # if not existing we create a new entry with some placeholders
            new_stores.append(
                Base_target.classes.app_dms_dimstore(
                    id = source_store.StoreID,
                    store_code = source_store.StoreCode,
                    store_name = source_store.StoreName,
                    store_display_label = source_store.StoreDisplayLabel,
                    iln = source_store.ILN,
                    city = source_store.City,
                    region_tax_rate = source_store.RegionTaxRate,
                    local_currency = source_store.LocalCurrency,
                    is_active = False,
                    dim_channel_id = dim_channel_placeholder_id,
                    dim_location_id = dim_location_placeholder_id
                )
            )

    if len(new_stores) > 0:
        session_target.bulk_save_objects(new_stores)

    print('Task completed successfully')
    print('Task duration: {} seconds, Updated: {}, Inserted: {}'.format(
        int((time.time() - start_time)), count_updated, len(new_stores)
    ))



def column_windows(session, column, windowsize):
    """Return a series of WHERE clauses against
    a given column that break it into windows.

    Result is an iterable of tuples, consisting of
    ((start, end), whereclause), where (start, end) are the ids.

    Requires a database that supports window functions,
    i.e. Postgresql, SQL Server, Oracle.

    Enhance this yourself !  Add a "where" argument
    so that windows of just a subset of rows can
    be computed.

    """
    def int_for_range(start_id, end_id):
        if end_id:
            return and_(
                column>=start_id,
                column<end_id
            )
        else:
            return column>=start_id

    q = session.query(
        column, func.row_number().over(order_by=column).label('rownum')
    ).from_self(column)

    if windowsize > 1:
        q = q.filter(sqlalchemy.text("rownum %% %d=1" % windowsize))

    intervals = [id for id, in q]

    while intervals:
        start = intervals.pop(0)
        if intervals:
            end = intervals[0]
        else:
            end = None
        yield int_for_range(start, end)

def windowed_query(q, column, windowsize):
    """"Break a Query into windows on a given column."""

    for whereclause in column_windows(q.session, column, windowsize):
        for row in q.filter(whereclause).order_by(column):
            yield row

def load_new_fact_movements():
    r"""
    Only load new Movements entries DMS load to IAP user input

    >>> generate_fact_movements(engine_source, engine_target)
    """

    start_time = time.time()
    print('Task - Load table dim_movements')

    Base = declarative_base()

    class Movements(Base):
        __tablename__ = 'Movements'

        MovementDate = Column(Date)
        MovementID = Column(String, primary_key=True)
        MovementType = Column(String)
        Units = Column(Integer)
        CostValue = Column(Float)
        SalesValue = Column(Float)
        MovementNumber = Column(String)
        MovementLine = Column(Integer)
        InsertDate = Column(DateTime)
        UpdateDate = Column(DateTime)
        InsertSource = Column(String)
        UpdateSource = Column(String)
        ProductID = Column(Integer)
        StoreID = Column(Integer)

    class FactMovements(Base):
        __tablename__ = 'app_dms_factmovements'

        movementdate= Column(Date, primary_key=True)
        movementid= Column(String, primary_key=True)
        movementtype=Column(String)
        units= Column(Integer)
        costvalue= Column(Float)
        salesvalue= Column(Float)
        movementnumber= Column(String)
        movementline= Column(Integer)
        insertdate= Column(DateTime)
        updatedate= Column(DateTime)
        insertsource= Column(String)
        updatesource= Column(String)
        dim_product_id= Column(Integer, primary_key=True)
        dim_store_id= Column(Integer, primary_key=True)
        dim_date_id= Column(Integer)

    # DMS
    session_source = Session_source()

    Base_target = automap_base()
    Base_target.prepare(engine_target, reflect=True)
    session_target = Session_target()

    # Query source and target
    # dim_date = session_target.query(Base_target.classes.app_dms_dimdate).all()
    # dim_date_full_date = {d.full_date:d.id for d in dim_date}

    # Set filter on source data date
    latest_dimdate = session_target.query(func.max(FactMovements.dim_date_id)).scalar()

    # Load the latest date delta
    movements = session_source.query(Movements).filter(
        Movements.MovementDate == datetime.datetime.strptime(str(latest_dimdate), '%Y%m%d')
    ).all()

    fact_movements = session_target.query(FactMovements).filter(
        FactMovements.movementdate == datetime.datetime.strptime(str(latest_dimdate), '%Y%m%d')
    ).all()

    fact_movements_keys = {(f.movementid, f.movementdate, f.dim_store_id, f.dim_product_id) for f in fact_movements}

    objects = list()

    for source_movement in movements:
        if (source_movement.MovementID,source_movement.MovementDate,source_movement.StoreID,source_movement.ProductID) not in fact_movements_keys:
            objects.append(
                FactMovements(
                    movementid=source_movement.MovementID,
                    movementdate=source_movement.MovementDate,
                    movementtype=source_movement.MovementType,
                    units=source_movement.Units,
                    costvalue=source_movement.CostValue,
                    salesvalue=source_movement.SalesValue,
                    movementnumber=source_movement.MovementNumber,
                    movementline=source_movement.MovementLine,
                    insertdate=source_movement.InsertDate,
                    updatedate=source_movement.UpdateDate,
                    insertsource=source_movement.InsertSource,
                    updatesource=source_movement.UpdateSource,
                    dim_product_id=source_movement.ProductID,
                    dim_store_id=source_movement.StoreID,
                    # dim_date_id=dim_date_full_date.get(source_movement.MovementDate, datetime.date(2000, 1, 1))
                    dim_date_id = int(str(source_movement.MovementDate).replace('-',''))
                )
            )

    # Load all the others
    q = session_source.query(Movements).filter(
        Movements.MovementDate > datetime.datetime.strptime(str(latest_dimdate), '%Y%m%d')
    )

    # Transfer data
    # for idx, source_movement in tqdm(enumerate(windowed_query(q, Movements.MovementID, 1000))):
    for source_movement in tqdm(q.all()):
        objects.append(
            FactMovements(
                movementid=source_movement.MovementID,
                movementdate=source_movement.MovementDate,
                movementtype=source_movement.MovementType,
                units=source_movement.Units,
                costvalue=source_movement.CostValue,
                salesvalue=source_movement.SalesValue,
                movementnumber=source_movement.MovementNumber,
                movementline=source_movement.MovementLine,
                insertdate=source_movement.InsertDate,
                updatedate=source_movement.UpdateDate,
                insertsource=source_movement.InsertSource,
                updatesource=source_movement.UpdateSource,
                dim_product_id=source_movement.ProductID,
                dim_store_id=source_movement.StoreID,
                # dim_date_id=dim_date_full_date.get(source_movement.MovementDate, datetime.date(2000, 1, 1))
                dim_date_id = int(str(source_movement.MovementDate).replace('-',''))
            )
        )

    session_target.bulk_save_objects(objects)

    print('Task completed successfully')
    print('Task duration: {} seconds, Inserted: {}'.format(
        int((time.time() - start_time)), len(objects)
    ))


def generate_staging_range_architecture(engine):
    r"""
    Generate staging_range_architecture
    """

    start_time = time.time()
    print('Task - Load table staging_range_architecture')

    # Base table
    iap_param_date_interval = cp.DICT_PARAMETER.get('iap_param_date_interval')
    staging_movement = pd.read_sql_query('''
        SELECT productid, units
        FROM staging_movement
        WHERE movementdate BETWEEN '{}' AND '{}'
    '''.format(iap_param_date_interval[0], iap_param_date_interval[1]), engine)

    # dim_product
    dim_product = pd.read_sql_query('''
        SELECT
            productid,
            division as product_group,
            essential_trend as product_essential_trend,
            basic_fashion as product_basic_fashion,
            category as product_category,
            style,
            style + colour as style_colour
        FROM dim_product
    ''', engine)
    staging_movement_exploded = pd.merge(staging_movement, dim_product, on='productid')

    # Range architecture with range_depth_ly
    final_df = staging_movement_exploded.groupby(
        ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category'], as_index=False
    ).agg({'units': pd.Series.count})

    # range_width_style_ly
    range_width_style_ly = staging_movement_exploded.groupby(
        ['product_group','product_essential_trend','product_basic_fashion','product_category']
    )['style'].nunique().reset_index()
    final_df = pd.merge(
        final_df, range_width_style_ly,
        how='inner',
        left_on=['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category'],
        right_on = ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category']
    )

    # range_width_style_colour_ly
    range_width_style_colour_ly = staging_movement_exploded.groupby(
        ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category']
    )['style_colour'].nunique().reset_index()
    final_df = pd.merge(
        final_df, range_width_style_colour_ly,
        how='inner',
        left_on=['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category'],
        right_on = ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category']
    )

    # Rename columns
    final_df = final_df.rename(columns={
        'units': 'range_depth_ly',
        'style': 'range_width_style_ly',
        'style_colour': 'range_width_style_colour_ly'
    })

    # Save to database (final_df)
    if final_df.empty:
        print('df is empty')
    else:
        final_df.to_sql('staging_range_architecture', engine, if_exists='replace', index=False)

    print('Task completed successfully')
    print('Task duration:', '%s seconds' % int((time.time() - start_time)))


def generate_staging_range_plan(engine):
    r"""
    Generate staging_range_plan
    """

    start_time = time.time()
    print('Task - Load table staging_range_plan')

    # Base table
    staging_range_master = pd.read_sql_query('''
        SELECT
            productcode
            product_group,
            product_category,
            essential_trend as product_essential_trend,
            basic_fashion as product_basic_fashion,
            article_no,
            style,
            colour,
            style + colour as style_colour
        FROM staging_range_master
    '''.format(), engine)

    # Correct fields
    col_mapping_dict = {
        'product_group': {
            'AC': '180 ACCESSORIES',
            'LI': '104 LINGERIE',
            'LW': '101 LEGWEAR',
            'RW': '102 READY-TO-WEAR',
            'SW': '103 SWIMWEAR',
            # '?': '190 ADV.+PROMOTION',
        },
        'product_category': {

        },
        'product_essential_trend': {
            'TREND': 'T',
            'NEW ESS': 'E',
        },
        'product_basic_fashion': {
            'FC': 'F',
            'BC': 'B',
        },
    }
    # staging_range_master = staging_range_master.replace(col_mapping_dict)
    staging_range_master['product_category'] = '110 TIGHTS (LW)'

    # Prepare final_df
    final_df = staging_range_master.groupby(
        ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category'], as_index=False
    )

    # range_width_style_ly
    range_width_style_ly = staging_range_master.groupby(
        ['product_group','product_essential_trend','product_basic_fashion','product_category']
    )['style'].nunique().reset_index()
    final_df = pd.merge(
        final_df, range_width_style_ly,
        how='inner',
        left_on=['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category'],
        right_on = ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category']
    )

    # range_width_style_colour_ly
    range_width_style_colour_ly = staging_range_master.groupby(
        ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category']
    )['style_colour'].nunique().reset_index()
    final_df = pd.merge(
        final_df, range_width_style_colour_ly,
        how='inner',
        left_on=['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category'],
        right_on = ['product_group', 'product_essential_trend', 'product_basic_fashion', 'product_category']
    )


    # Save to database (final_df)
    if final_df.empty:
        print('df is empty')
    else:
        final_df.to_sql('staging_range_plan', engine, if_exists='replace', index=False)

    print('Task completed successfully')
    print('Task duration:', '%s seconds' % int((time.time() - start_time)))


def generate_report_cluster_store(engine):
    r"""
    Generate report_cluster_store
    """

    start_time = time.time()
    print('Task - Load table report_cluster_store')

    # staging_movement
    staging_movement_with_date = pd.read_sql_query('''
        SELECT productid, sales_year, sales_season, storeid, productid, units
        FROM
            staging_movement sm
            INNER JOIN
            (
            SELECT
                full_date,
                sales_year,
                sales_season
            FROM dim_date
            WHERE sales_year >= {}
            ) dd
                ON sm.movementdate = dd.full_date
    '''.format(2016), engine)

    # dim_date
    # dim_date = pd.read_sql_query('''
    #     SELECT
    #         id,
    #         full_date,
    #         sales_year,
    #         sales_season
    #     FROM dim_date
    # ''', engine)

    # dim_store
    dim_store = pd.read_sql_query('''
        SELECT
            store_id,
            store_code,
            store_name,
            store_type,
            store_active,
            store_size,
            store_location,
            store_style,
            customer_type,
            net_retail_sales_in_eur_ty,
            average_monthly_sales_for_ty,
            region,
            country,
            city,
            potential,
            store_tier,
        FROM dim_store
    ''', engine)

    # dim_product
    dim_product = pd.read_sql_query('''
        SELECT
            productid,
            division as product_group
        FROM dim_product
    ''', engine)

    # Merge staging_movement and dim_date
    # final_df = pd.merge(staging_movement, dim_date, how='inner',
    #     left_on=['movementdate'],
    #     right_on = ['full_date']
    # )

    # Group by sales_year, sales_season for sales_volume_ty (later relative_sales_volume_ty)
    final_df = final_df.groupby(
        ['sales_year', 'sales_season'], as_index=False
    ).agg({'units': pd.Series.count})
    final_df = final_df.rename(columns={
        'units': 'sales_volume_ty'
    })

    # Merge with dim_store
    final_df = pd.merge(
        final_df, dim_store,
        how='inner',
        left_on=['storeid'],
        right_on = ['store_id']
    )

    # final_df = pd.merge(final_df, dim_product, on='productid')
    # sku_count,
    # relative_sales_volume_ty,
    # average_value_transaction,
    # sales_lingerie,
    # sales_legwear,
    # sales_ready_to_wear,
    # sales_adv_promotion,
    # sales_accessories

    # Save to database (final_df)
    if final_df.empty:
        print('df is empty')
    else:
        final_df.to_sql('report_cluster_store_test', engine, if_exists='replace', index=False)

    print('Task completed successfully')
    print('Task duration:', '%s seconds' % int((time.time() - start_time)))
