import sqlite3 as sql

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(BASE_DIR, "..", "torosweb", "dev_db.sqlite3")
conn = sql.connect(db_path)
cursor = conn.cursor()

#Delete all entries
cursor.execute("DELETE FROM broker_sourcecatalog;")
conn.commit()

# Find the column order as it is layed on the database
col_order = [c[1] for c in cursor.execute('pragma table_info(broker_sourcecatalog);')]

# First row of GLADE 2.3 txt
# 2789 NGC0253 NGC0253 00473313-2517196 null G 11.88806 -25.288799
# 3.92595099046 null 0.00091602045801 7.34 0.30 null 4.874 0.015 4.143
# 0.015 3.822 0.016 3 0

glade_path = os.path.join(BASE_DIR, "Catalogs", "GLADE_2.3_no_dups.txt")
gladefp = open(glade_path)
gladename_unique = set()
for ind, aline in enumerate(gladefp.readlines()):
    (pgc, gwgc_name, hyperleda_name, twoMASS_name, sdss_dr12_name,
    obj_type, ra, dec, dist, dist_err, z_redshift,
    b_mag, b_err, b_abs, j_mag, j_err,
    h_mag, h_err, k_mag, k_err,
    dist_flag, velocity_flag) = aline.split()

    kw = {}
    kw['pgc'] = int(pgc) if pgc != 'null' else None

    # Pick gwgc or > hyperlida > twoMASS > sdss
    if sdss_dr12_name != 'null':
        kw['name'] = sdss_dr12_name
    if twoMASS_name != 'null':
        kw['name'] = twoMASS_name
    if hyperleda_name != 'null':
        kw['name'] = hyperleda_name
    if gwgc_name != 'null':
        kw['name'] = gwgc_name

    # Don't add if it's already included
    if kw['name'] in gladename_unique:
        continue
    gladename_unique.add(kw['name'])

    kw['obj_type'] = obj_type if obj_type != 'null' else None
    kw['ra'] = float(ra) if ra != 'null' else None
    kw['dec'] = float(dec) if dec != 'null' else None
    kw['dist'] = float(dist) if dist != 'null' else None
    kw['dist_err'] = float(dist_err) if dist_err != 'null' else None
    kw['b_mag'] = float(b_mag) if b_mag != 'null' else None
    kw['b_err'] = float(b_err) if b_err != 'null' else None
    kw['b_abs'] = float(b_abs) if b_abs != 'null' else None
    kw['j_mag'] = float(j_mag) if j_mag != 'null' else None
    kw['j_err'] = float(j_err) if j_err != 'null' else None
    kw['h_mag'] = float(h_mag) if h_mag != 'null' else None
    kw['h_err'] = float(h_err) if h_err != 'null' else None
    kw['k_mag'] = float(k_mag) if k_mag != 'null' else None
    kw['k_err'] = float(k_err) if k_err != 'null' else None

    if ind % 100_000 == 0:
        print("Element {} of 3,200,000+".format(ind))

    entry = tuple(kw.get(key) for key in col_order)
    cursor.execute("insert into broker_sourcecatalog values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", entry)
conn.commit()
gladefp.close()

print("Loading GWGC objects missing in GLADE")
gwgc_missing_fpath = os.path.join(BASE_DIR, "Catalogs", "glade_missing.txt")
missingfp = open(gwgc_missing_fpath, "r")
for aline in missingfp.readlines():
    if aline[0] == "#":
        continue
    (pgc, name, ra, dec, obj_type, bmag, a, a_err, b, b_err, b_over_a,
         b_over_a_err, pa, babs, dist, dist_err,
         bmag_err, abs_mag_err) = aline.split()
    kw = {}
    kw['pgc'] = int(pgc) if pgc != 'None' else None
    kw['name'] = name if name != 'None' else None
    kw['ra'] = (float(ra) * 15.0) % 360.0 if ra != 'None' else None
    kw['dec'] = float(dec) if dec != 'None' else None
    kw['obj_type'] = 'U'
    kw['b_mag'] = float(bmag) if bmag != 'None' else None
    kw['b_err'] = float(bmag_err) if bmag_err != 'None' else None
    kw['b_abs']= float(babs) if babs != 'None' else None
    kw['dist'] = float(dist) if dist != 'None' else None
    kw['dist_err'] = float(dist_err) if dist_err != 'None' else None

    entry = tuple(kw.get(key) for key in col_order)
    cursor.execute("insert into broker_sourcecatalog values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", entry)
conn.commit()
missingfp.close()