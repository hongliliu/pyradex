from astropy import units as u
import sys
import os
import errno
from astropy import log

def mkdir_p(path):
    """ mkdir -p equivalent [used by get_datafile]"""
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def united(qty, unit):
    if isinstance(qty,u.Quantity):
        return qty.to(unit)
    else:
        return qty*u.Unit(unit)

def uvalue(qty, unit):
    return united(qty, unit).value

def get_datafile(species, savedir='./'):
    """
    Load a molecular data file and save it into the specified directory
    """
    from astroquery import lamda

    datapath = os.path.join(savedir,species)

    species,suffix = os.path.splitext(species)
    if suffix == "":
        datapath += ".dat"
    elif suffix != ".dat":
        raise ValueError("Molecular data file must either be a species name or species.dat")

    if not os.path.isdir(savedir):
        mkdir_p(savedir)

    if not os.path.isfile(datapath):
        data = lamda.query(species, return_datafile=True)
        with open(datapath,'w') as out:
            out.writelines([d+"\n" for d in data])

    return os.path.split(datapath)

def get_colliders(fn):
    """
    Get the list of colliders in a LAMDA data file
    """
    from astroquery import lamda

    collrates,radtrans,enlevs = lamda.core.parse_lamda_datafile(fn)
    colliders = collrates.keys()

    return colliders


def verify_collisionratefile(fn):
    """
    Verify that a RADEX collisional rate file is valid to avoid a RADEX crash
    """
    from astroquery import lamda

    if not os.path.exists(fn):
        raise IOError("File {0} does not exist.".format(fn))

    for qt in lamda.core.query_types:
        try:
            collrates,radtrans,enlevs = lamda.core.parse_lamda_datafile(fn)
        except Exception as ex:
            raise type(ex), type(ex)("Data file verification failed.  The molecular data file may be corrupt." +
                                     "\nOriginal Error in the parser: " +
                                     ex.args[0]), sys.exc_info()[2]
        if len(collrates) == 0:
            raise ValueError("No data found in the table for the category %s" % qt)

class QuantityOff(object):
    """ Context manager to disable quantities """
    def __enter__(self):
        self._quantity = u.Quantity
        u.Quantity = lambda value,unit: value

    def __exit__(self, type, value, traceback):
        u.Quantity = self._quantity
 
class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise AttributeError("Setting items for this dictionary is not supported.")

def unitless(x):
    if hasattr(x, 'value'):
        return x.value
    else:
        return x

# silly tool needed for fortran misrepresentation of strings
# http://stackoverflow.com/questions/434287/what-is-the-most-pythonic-way-to-iterate-over-a-list-in-chunks
def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return itertools.izip_longest(*args, fillvalue=fillvalue)

def lower_keys(d):
    """ copy dictionary with lower-case keys """
    return {k.lower(): k[d] for k in d}
