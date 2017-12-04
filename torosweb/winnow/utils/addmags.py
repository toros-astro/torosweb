"""
Upload magnitud to existing objects
   
   University of Texas at San Antonio
"""

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'torosweb.settings')
import django
django.setup()
from winnow.models import TransientCandidate, SEPInfo

if __name__ == '__main__':
    import numpy as np
    import os
    import sep
    from astropy.io import fits
    import numpy as np
    import toros

    magzero = fits.getval('151K5947_diff.fits', 'magzero')
    orig_image = fits.getdata("151K5947.fits").astype('float32')
    orig_header = fits.getheader("151K5947_diff.fits")
    bkg = sep.Background(orig_image)

    ref_data = toros.skygoldmaster.getReference(orig_image, orig_header, reference_fits_file="master2010.fits")
    ref_image = ref_data.filled(fill_value=np.median(ref_data))
    bkg_ref = sep.Background(ref_image)

    #hdu = fits.PrimaryHDU(ref_image, header=orig_header)
    #hdu.writeto("151K5947_ref.fits", clobber=True)

    subt_image = fits.getdata('151K5947_diff.fits').astype('float32')

    def findMagnitude(x, y, data, bkg, magzero, apRadius=5):
      fl, __, __     = sep.apercirc(data, x, y, apRadius)
      fl = fl.item()
      if bkg is not None:
        fl_bkg, __, __ = sep.apercirc(bkg, x, y, apRadius)
        fl_bkg = fl_bkg.item()
      else:
        fl_bkg = 0.
      flux = fl - fl_bkg
      if flux > 1.:
        mag = -2.5*np.log10(flux) + magzero
      else:
        mag = -1.
      return mag

    for tc in TransientCandidate.objects.filter(dataset_id='first_cstar_diff'):
      sepinfo = SEPInfo.objects.get(trans_candidate=tc)
      x, y = sepinfo.x, sepinfo.y
      tc.mag_orig = findMagnitude(x,y,orig_image,bkg.back(),magzero,5)
      tc.mag_ref  = findMagnitude(x,y,ref_image,bkg_ref.back(),magzero,5)
      tc.mag_subt = findMagnitude(x,y,subt_image,None,magzero,5)
      tc.save()




