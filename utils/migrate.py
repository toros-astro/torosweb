# Migrate users:
import sqlite3 as sql
import collections 
conn_old = sql.connect('db_production.sqlite3')
c_old = conn_old.cursor()
conn_new = sql.connect('dev_db.sqlite3')
c_new = conn_new.cursor()


new_site_id = c_new.execute(
    "select * from django_site where id = (select max(ID) from django_site);")\
    .fetchone()[0]


# This is to quickly switch between ctypes 
old_ctype_cols = [v[1] for v in c_old.execute('pragma table_info(django_content_type);')]
app_label_col = old_ctype_cols.index('app_label')
model_col = old_ctype_cols.index('model')
id_col = old_ctype_cols.index('id')
old_ctype = {entry[id_col]: "_".join([entry[app_label_col], entry[model_col]]) \
                for entry in c_old.execute("select * from django_content_type")}
new_ctype_cols = [v[1] for v in c_new.execute('pragma table_info(django_content_type);')]
app_label_col = new_ctype_cols.index('app_label')
model_col = new_ctype_cols.index('model')
id_col = new_ctype_cols.index('id')
new_ctype = {"_".join([entry[app_label_col], entry[model_col]]): entry[id_col] \
                for entry in c_new.execute("select * from django_content_type")}


# This is to quickly switch between group id's
old_group_cols = [v[1] for v in c_old.execute('pragma table_info(auth_group);')]
name_col = old_group_cols.index('name')
id_col = old_group_cols.index('id')
old_gid = {entry[id_col]: entry[name_col] \
                for entry in c_old.execute("select * from auth_group")}
new_group_cols = [v[1] for v in c_new.execute('pragma table_info(auth_group);')]
name_col = new_group_cols.index('name')
id_col = new_group_cols.index('id')
new_gid = {entry[name_col]: entry[id_col]\
                for entry in c_new.execute("select * from auth_group")}


def migrate_users():
    for auser in c_old.execute("select * from auth_user"):
        u_id, u_pwd, u_last_login, u_is_superuser, u_first_name,\
        u_last_name, u_email, u_is_staff, u_is_active, u_date_joined,\
        u_username = auser
        migrated_user = (u_id, u_pwd, u_last_login, u_is_superuser, u_username,\
        u_first_name, u_last_name, u_email, u_is_staff, u_is_active, u_date_joined,\
        'OTHER', '')
        c_new.execute('insert into account_user values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', migrated_user)
    conn_new.commit()


def migrate_broker():
    for table_name in ("observatory", "alert", "assignment"):
        old_keys = {v[1]: k for k, v in enumerate(
            c_old.execute('pragma table_info(broker_{});'.format(table_name)))}
        new_keys = {k: v[1] for k, v in enumerate(
            c_new.execute('pragma table_info(broker_{});'.format(table_name)))}
        for anitem in c_old.execute("select * from broker_{}".format(table_name)):
            anitem_reorder = tuple(anitem[old_keys[new_keys[k]]] for k in range(len(new_keys)))
            quest_marks = '?, ' * (len(anitem_reorder) - 1)
            c_new.execute('insert into broker_{} values ({}?)'\
                .format(table_name, quest_marks), anitem_reorder)
        conn_new.commit()


def migrate_winnow():
    for table_name in ("dataset", "transientcandidate", "sepinfo", "ranking"):
        old_keys = {v[1]: k for k, v in enumerate(
            c_old.execute('pragma table_info(winnow_{});'.format(table_name)))}
        new_keys = {k: v[1] for k, v in enumerate(
            c_new.execute('pragma table_info(winnow_{});'.format(table_name)))}
        for anitem in c_old.execute("select * from winnow_{}".format(table_name)):
            anitem_reorder = tuple(anitem[old_keys[new_keys[k]]] for k in range(len(new_keys)))
            quest_marks = '?, ' * (len(anitem_reorder) - 1)
            c_new.execute('insert into winnow_{} values ({}?)'\
                .format(table_name, quest_marks), anitem_reorder)
        conn_new.commit()


def migrate_rbmanager():
    for table_name in ("feature", "experiment_features", "experiment"):
        old_keys = {v[1]: k for k, v in enumerate(
            c_old.execute('pragma table_info(rbmanager_{});'.format(table_name)))}
        new_keys = {k: v[1] for k, v in enumerate(
            c_new.execute('pragma table_info(winnow_{});'.format(table_name)))}
        for anitem in c_old.execute("select * from rbmanager_{}".format(table_name)):
            anitem_reorder = tuple(anitem[old_keys[new_keys[k]]] for k in range(len(new_keys)))
            quest_marks = '?, ' * (len(anitem_reorder) - 1)
            c_new.execute('insert into winnow_{} values ({}?)'\
                .format(table_name, quest_marks), anitem_reorder)
        conn_new.commit()


def migrate_wiki():
    regular_wiki_tables = ['wiki_reusableplugin', 
        'wiki_reusableplugin_articles', 'wiki_revisionpluginrevision',
        'wiki_simpleplugin', 'wiki_revisionplugin', 'wiki_articlerevision',
        'wiki_articleplugin', 'wiki_attachments_attachmentrevision',
        'wiki_attachments_attachment', 'wiki_images_image',
        'wiki_images_imagerevision', 'wiki_notifications_articlesubscription',
        'wiki_urlpath', 'wiki_articleforobject', 'wiki_article']

    for table_name in regular_wiki_tables:
        old_keys = {v[1]: k for k, v in enumerate(
            c_old.execute('pragma table_info({});'.format(table_name)))}
        col_names_new = [v[1] for v in c_new.execute('pragma table_info({});'\
            .format(table_name))]
        new_keys = {k: v for k, v in enumerate(col_names_new)}
        for anitem in c_old.execute("select * from {}".format(table_name)):
            anitem_reorder = [anitem[old_keys[new_keys[k]]] 
                if new_keys[k] in old_keys else None 
                for k in range(len(new_keys))]

            # If any of the columns is site_id replace with new site_id
            if 'site_id' in col_names_new:
                site_id_col = col_names_new.index('site_id')
                anitem_reorder[site_id_col] = new_site_id

            # If any of the columns is content_type replace accordingly
            if 'content_type_id' in col_names_new:
                ct_fk_old = anitem[old_keys['content_type_id']]
                ct_col_in_new = col_names_new.index('content_type_id')
                anitem_reorder[ct_col_in_new] = new_ctype[old_ctype[ct_fk_old]]

            # If any of the columns is group_id replace accordingly
            if 'group_id' in col_names_new:
                gid_fk_old = anitem[old_keys['group_id']]
                gid_col_in_new = col_names_new.index('group_id')
                anitem_reorder[gid_col_in_new] = new_gid[old_gid[gid_fk_old]]

            quest_marks = '?, ' * (len(anitem_reorder) - 1)
            c_new.execute('insert into {} values ({}?)'\
                .format(table_name, quest_marks), anitem_reorder)
        conn_new.commit()


def migrate_django_comments():
    old_keys = {v[1]: k for k, v in enumerate(
        c_old.execute('pragma table_info(django_comments);'))}
    col_names_new = [v[1] for v in c_new.execute('pragma table_info(django_comments);')]
    new_keys = {k: v for k, v in enumerate(col_names_new)}

    for anitem in c_old.execute("select * from django_comments"):
        anitem_reorder = [anitem[old_keys[new_keys[k]]] for k in range(len(new_keys))]

        # Change the index of content_type_id by the corresponding content_type_id in the new db

        # If any of the columns is site_id replace with new site_id
        if 'site_id' in col_names_new:
            site_id_col = col_names_new.index('site_id')
            anitem_reorder[site_id_col] = new_site_id

        if 'content_type_id' in col_names_new:
            # Assign the new ctype foreign key to its place in the item reordered
            ct_fk_old = anitem[old_keys['content_type_id']]
            ct_col_in_new = col_names_new.index('content_type_id')
            anitem_reorder[ct_col_in_new] = new_ctype[old_ctype[ct_fk_old]]

        anitem_reorder = tuple(anitem_reorder)
        quest_marks = '?, ' * (len(anitem_reorder) - 1)
        c_new.execute('insert into django_comments values ({}?)'\
                      .format(quest_marks), anitem_reorder)
    conn_new.commit()


if __name__ == '__main__':
    migrate_users()
    migrate_broker()
    migrate_winnow()
    migrate_rbmanager()
    migrate_wiki()
    migrate_django_comments()
    conn_new.close()
    conn_old.close()
