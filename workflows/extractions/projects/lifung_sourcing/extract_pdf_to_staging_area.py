import os
import numpy as np
import pandas as pd
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import ForeignKey, create_engine, UniqueConstraint, schema, types, update, and_
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool
from sqlalchemy.types import Integer, VARCHAR, Float, Date, DateTime
from urllib.parse import quote_plus

from django.conf import settings as cp


def pdf_exists(file_property):

    source_master_reference = file_property['name'] + file_property['extension']
    source_metadata_last_modified_dt = datetime.fromtimestamp(os.path.getmtime(file_property['abs_path']))

    # Look if file_name is in source_master table
    master = session.query(SourceMaster)\
                    .filter(SourceMaster.reference == source_master_reference)\
                    .first()

    if master is None:
        return False

    # Look if metadata exists
    metadata = session.query(SourceMetadata)\
                .filter(
                    SourceMetadata.source_master_id == master.id
                ).first()


    if metadata is None or metadata.last_modified_dt < source_metadata_last_modified_dt:
        return False

    return True


def load_to_staging_area(session, base, database_atoms, ignore_meta=False):
    """ Load data to database

    entries -- list of dictionaries, each representing an entry to insert into the database
    """
    classes = base.classes

    SourceData = classes.app_staging_area_sourcedata
    SourceHeader = classes.app_staging_area_sourceheader
    SourceMaster = classes.app_staging_area_sourcemaster
    SourceMasterComponent = classes.app_staging_area_sourcemastercomponent
    SourceMetadata = classes.app_staging_area_sourcemetadata
    SourceMetadataFile = classes.app_staging_area_sourcemetadatafile

    metadata_exists = True
    insertions = 0

    source_master_component_category = database_atoms[0]['source_master_component_category']
    source_master_reference = database_atoms[0]['source_master_reference']
    has_data = database_atoms[0]['has_data']

    # Look if file_name is in source_master table
    master = session.query(SourceMaster)\
                    .filter(SourceMaster.reference == database_atoms[0]['source_master_reference'])\
                    .first()

    if master is None:
        # Add new metadata entry
        master = SourceMaster(
            name = database_atoms[0]['source_master_name'],
            label = database_atoms[0]['source_master_label'],
            reference = database_atoms[0]['source_master_reference'],
            pattern = database_atoms[0]['source_master_pattern']
        )

        session.add(master)
        session.commit()
        master = session.query(SourceMaster)\
                    .filter(SourceMaster.reference == database_atoms[0]['source_master_reference'])\
                    .first()

    # Look if metadata exists
    metadata = session.query(SourceMetadata)\
                .filter(
                    SourceMetadata.source_master_id == master.id
                ).first()

    if metadata is None:
        metadata_exists = False
        insertions += 1
        # Add new metadata
        metadata = SourceMetadata(
            source_master_id = master.id,
            name = master.name,
            field_format = database_atoms[0]['source_metadata_field_format'],
            last_modified_dt = database_atoms[0]['source_metadata_last_modified_dt'],
            last_modified_by = database_atoms[0]['source_metadata_last_modified_by']
        )

        session.add(metadata)
        session.commit()
        metadata = session.query(SourceMetadata)\
                .filter(
                    SourceMetadata.source_master_id == master.id,
                    SourceMetadata.last_modified_dt == database_atoms[0]['source_metadata_last_modified_dt']
                ).first()

        # Add new metadata_file
        metadata_file = SourceMetadataFile(
            source_metadata_id = metadata.id,
            relative_path = database_atoms[0]['source_metadata_file_relative_path'],
            absolute_path = database_atoms[0]['source_metadata_file_absolute_path'],
            size = database_atoms[0]['source_metadata_file_size'],
            creation_dt = database_atoms[0]['source_metadata_file_creation_dt']
        )

        session.add(metadata_file)
        session.commit()

    elif metadata.last_modified_dt < database_atoms[0]['source_metadata_last_modified_dt']:
        # Update
        metadata.last_modified_dt = database_atoms[0]['source_metadata_last_modified_dt']

        metadata_file = session.query(SourceMetadataFile)\
                .filter(
                    SourceMetadataFile.source_metadata_id == metadata.id
                ).first()

        metadata_file.relative_path = database_atoms[0]['source_metadata_file_relative_path']
        metadata_file.absolute_path = database_atoms[0]['source_metadata_file_absolute_path']
        metadata_file.size = database_atoms[0]['source_metadata_file_size']
        metadata_file.creation_dt = database_atoms[0]['source_metadata_file_creation_dt']

        session.commit()

    # Create master_component if not existing for the given version of the file
    if not ignore_meta:
        master_component = session.query(SourceMasterComponent)\
                            .filter(
                                SourceMasterComponent.source_master_id == master.id,
                                SourceMasterComponent.category == database_atoms[0]['source_master_component_category']
                            ).first()

    if ignore_meta or master_component is None:

        if database_atoms[0]['source_master_component_category'] == 'graphic':
            filtered_database_atoms = database_atoms
        else:
            filtered_database_atoms = [database_atoms[0]]

        master_components = list()
        for database_atom in filtered_database_atoms:
            # Add new master_component
            master_components.append(SourceMasterComponent(
                source_master_id = master.id,
                category = database_atom['source_master_component_category'],
                reference = database_atom['source_master_component_reference'],
                name = database_atom['source_master_component_name'],
                label = database_atom['source_master_component_label']
            ))

        session.bulk_save_objects(master_components)
        session.commit()

    # Create headers for this table if not existing

    source_data_entries = list()
    headers = list()

    if has_data and source_master_component_category in ('table', 'tuple'):

        master_component = session.query(SourceMasterComponent).filter(
            SourceMasterComponent.source_master_id == master.id,
            SourceMasterComponent.category == database_atoms[0]['source_master_component_category'],
            SourceMasterComponent.name == database_atoms[0]['source_master_component_name'],
        ).first()

        for table_atom in database_atoms:

            header = session.query(SourceHeader).filter(
                SourceHeader.source_master_component_id == master_component.id,
                SourceHeader.name == table_atom['source_header_name']
            ).first()

            if header is None:
                # Add new header
                header = SourceHeader(
                    source_master_component_id = master_component.id,
                    name = table_atom['source_header_name'],
                    label = table_atom['source_header_label'],
                    data_type = table_atom['source_header_data_type']
                )

                headers.append(header)

                session.add(header)
                session.commit()


                header = session.query(SourceHeader)\
                    .filter(
                        SourceHeader.source_master_component_id == master_component.id,
                        SourceHeader.name == table_atom['source_header_name'],
                    ).first()



            # source_data = session.query(SourceData)\
            #         .filter(
            #             SourceData.source_metadata_id == metadata.id,
            #             SourceData.source_header_id == header.id,
            #             SourceData.row_number == table_atom['source_data_row_number']
            #         ).first()
            #
            # if source_data is None:
            # Add data!
            if ignore_meta or not metadata_exists:
                source_data_entries.append(
                    SourceData(
                        source_header_id = header.id,
                        source_metadata_id = metadata.id,
                        category = table_atom['source_data_category'],
                        row_number = table_atom['source_data_row_number'],
                        value = table_atom['source_data_value']
                    )
                )
            # else:
            #     source_data.category = table_atom['source_data_category'],
            #     source_data.row_number = table_atom['source_data_row_number'],
            #     source_data.value = table_atom['source_data_value']

        if len(source_data_entries) > 0:
            session.bulk_save_objects(source_data_entries)
        session.commit()

    return len(source_data_entries)
