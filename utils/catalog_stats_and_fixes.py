
# First row 
# PGC   Name   RA   Dec   Type   App_Mag   Maj_Diam_a   err_Maj_Diam   
# Min_Diam_b   err_Min_Diam   b/a   err_b/a   PA   Abs_Mag   Dist   err_Dist
# err_App_Mag   err_Abs_Mag

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

gwgc_all = []
gwgc_unique = set()
gwgc_dups = []
gwgc_path = os.path.join(BASE_DIR, "Catalogs", "GWGCCatalog.txt")
with open(gwgc_path, "r") as fp:
    for aline in fp.readlines():
        if aline[0] == "#":
            continue
        (pgc, name, ra, dec, obj_type, app_mag, a, a_err, b, b_err, b_over_a,
         b_over_a_err, pa, abs_mag, dist, dist_err,
         app_mag_err, abs_mag_err) = aline.split()
        gwgc_all.append(name)
        if name in gwgc_unique:
            gwgc_dups.append(name)
        gwgc_unique.add(name)


print("Statistics will be saved to statistics_summary.txt")
fpout = open(os.path.join(BASE_DIR, "statistics_summary.txt"), "w")

fpout.write("GWGC Statistics\n")
fpout.write("===============\n")
fpout.write("Total number of objects: {}\n".format(len(gwgc_all)))
fpout.write("Unique objects: {}\n".format(len(gwgc_unique)))
fpout.write("Duplicated objects: {}\n".format(len(gwgc_dups)))
if gwgc_dups:
    fpout.write(gwgc_dups.__str__())
    fpout.write("\n")
fpout.write("\n\n")

# First row of GLADE 2.3 txt
# 2789 NGC0253 NGC0253 00473313-2517196 null G 11.88806 -25.288799
# 3.92595099046 null 0.00091602045801 7.34 0.30 null 4.874 0.015 4.143
# 0.015 3.822 0.016 3 0

glade_all = []
glade_unique = set()
glade_dups = set()
gwgc_in_glade = set()
twoMASS_objs = 0
max_len = 0
neg_dist = []
null_dist = null_dist_no_z = 0
glade_path = os.path.join(BASE_DIR, "Catalogs", "GLADE_2.3.txt")

gwgcglade_unique = set()
hyperleda_unique = set()
twoMASS_unique = set()
sdss_unique = set()
glade_dup_entries = set()

with open(glade_path, "r") as fp:
    for index, aline in enumerate(fp.readlines()):
        if aline[0] == "#":
            continue
        (pgc, gwgc_name, hyperleda_name, twoMASS_name, sdss_dr12_name,
        obj_type, ra, dec, dist, dist_err, z_redshift,
        b_mag, b_err, b_abs, j_mag, j_err,
        h_mag, h_err, k_mag, k_err,
        dist_flag, velocity_flag) = aline.split()

        max_len = max(max_len, len(gwgc_name), len(hyperleda_name), len(twoMASS_name), len(sdss_dr12_name))

        if dist == 'null':
            null_dist += 1
            if z_redshift == 'null':
                null_dist_no_z += 1
        elif float(dist) < 0.0:
            neg_dist.append((index, float(dist)))

        # Pick gwgc or > hyperlida > twoMASS > sdss
        name = 'null'
        if sdss_dr12_name != 'null':
            name = sdss_dr12_name
            if sdss_dr12_name in sdss_unique:
                glade_dup_entries.add(index + 1)
            sdss_unique.add(sdss_dr12_name)
        if twoMASS_name != 'null':
            name = twoMASS_name
            if twoMASS_name in twoMASS_unique:
                glade_dup_entries.add(index + 1)
            twoMASS_unique.add(twoMASS_name)
        if hyperleda_name != 'null':
            name = hyperleda_name
            if hyperleda_name in hyperleda_unique:
                glade_dup_entries.add(index + 1)
            hyperleda_unique.add(hyperleda_name)
        if gwgc_name != 'null':
            name = gwgc_name
            if gwgc_name in gwgcglade_unique:
                glade_dup_entries.add(index + 1)
            gwgcglade_unique.add(gwgc_name)
        glade_all.append(name)
        if name in glade_unique:
            glade_dups.add(name)
        glade_unique.add(name)

        if gwgc_name != 'null':
            gwgc_in_glade.add(gwgc_name)

        if twoMASS_name != 'null':
            twoMASS_objs += 1

fpout.write("GLADE Statistics\n")
fpout.write("================\n")
fpout.write("There are {} objects with null distance.\n".format(null_dist))
fpout.write("From those, {} don't have z info either\n".format(null_dist_no_z))
if null_dist and null_dist < 50:
    fpout.write("Entries with null distance:\n")
    fpout.write(null_dist.__str__())
    fpout.write("\n")
fpout.write("There are {} objects with negative distance.\n".format(len(neg_dist)))
if neg_dist and len(neg_dist) < 50:
    fpout.write("Entries with negative distance\n")
    fpout.write(neg_dist.__str__())
    fpout.write("\n")
fpout.write("Maximum length of any name is {}\n".format(max_len))
fpout.write("There are {} 2MASS objects in GLADE\n".format(twoMASS_objs))
fpout.write("Is GWGC in GLADE a strict subset of GWGC?: {}\n".format(gwgc_in_glade <= gwgc_unique))
gwgc_missing_in_glade = gwgc_unique - gwgc_in_glade
if len(gwgc_missing_in_glade) > 0:
    fpout.write("There are {} GWGC objects missing from GLADE.\n".format(len(gwgc_missing_in_glade)))
    if len(gwgc_missing_in_glade) < 30:
        fpout.write(list(gwgc_missing_in_glade).__str__())
        fpout.write("\n")
fpout.write("There are (at least) {} duplicated objects in GLADE.\n".format(len(glade_dup_entries)))
fpout.close()

missing_fname = os.path.join(BASE_DIR, "Catalogs", "glade_missing.txt")
print("GWGC objects missing in GLADE will be saved to Catalogs/{}".format(os.path.basename(missing_fname)))
fpmiss = open(missing_fname, "w")
with open(gwgc_path, "r") as fp:
    for aline in fp.readlines():
        name = aline.split()[1]
        if name in gwgc_missing_in_glade:
            fpmiss.write(aline)
fpmiss.close()

glade_nodups_fname = os.path.join(BASE_DIR, "Catalogs", "GLADE_2.3_no_dups.txt")
print("Saving GLADE catalog with duplicates removed to Catalogs/{}".format(os.path.basename(glade_nodups_fname)))
fpout = open(glade_nodups_fname, "w")
with open(glade_path) as fp:
    for index, aline in enumerate(fp.readlines()):
        if not ((index + 1) in glade_dup_entries):
            fpout.write(aline)
fpout.close()
