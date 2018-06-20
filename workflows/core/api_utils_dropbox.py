def get_file_name_list(username):
    """
    Get list of all dropbox files for specific username folder using API v2
    """
    dbx = dropbox.Dropbox(cp.DROPBOX_ACCESS_TOKEN)

    file_list = list()
    try:
        for entry in dbx.files_list_folder(cp.STATIC_URL + '/users/' + username, recursive=True).entries:
            file_list.append(entry.name)
    except dropbox.exceptions.ApiError:
        return []

    return file_list


def get_file_shared_link(username, file_name):
    """
    Get dropbox url to share for file path using API v2
    """
    dbx = dropbox.Dropbox(cp.DROPBOX_ACCESS_TOKEN)
    file_path = cp.STATIC_URL + 'users/' + username + '/' + file_name

    try:
        shared_link_metadata = dbx.sharing_create_shared_link(file_path, short_url=True)
    except dropbox.exceptions.ApiError:
        return None

    return shared_link_metadata.url


def upload_file(username, file_name):
    """
    Upload a file to dropbox using API v2
    """
    dbx = dropbox.Dropbox(cp.DROPBOX_ACCESS_TOKEN)

    write_mode = 'overwrite' if file_name in get_file_name_list(username) else 'add'
    file_to = cp.STATIC_URL + 'users/' + username + '/' + file_name

    try:
        with open(os.path.join(cp.STATIC_FILE_PATH, username, file_name), 'rb') as f:
            dbx.files_upload(f.read(), file_to, mode=dropbox.files.WriteMode(write_mode, None))
    except dropbox.exceptions.ApiError:
        return None
