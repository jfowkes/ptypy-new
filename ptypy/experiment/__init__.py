# -*- coding: utf-8 -*-
"""
Beamline-specific data preparation modules.

Currently available:
 * I13DLS, FFP and NFP
 * I08DLS, FFP and NFP
 * ID16A ESRF, NFP
 * AMO LCLS
 * DiProI FERMI
 * NanoMAX

This file is part of the PTYPY package.

    :copyright: Copyright 2014 by the PTYPY team, see AUTHORS.
    :license: GPLv2, see LICENSE for details.
"""
# Import instrument-specific modules
#import cSAXS

from I13_ffp import I13ScanFFP
from I13_nfp import I13ScanNFP
from DLS import DlsScan
from I08 import I08Scan
from savu import Savu
from plugin import makeScanPlugin
from ID16Anfp import ID16AScan
from AMO_LCLS import AMOScan
from DiProI_FERMI import DiProIFERMIScan
from optiklabor import FliSpecScanMultexp
from UCL import UCLLaserScan
from nanomax import NanomaxStepscanNov2016, NanomaxStepscanMay2017, NanomaxFlyscanJune2017
from ALS_5321 import ALS5321Scan


if __name__ == "__main__":
    from ptypy.utils.verbose import logger
    from ptypy.core.data import PtydScan, MoonFlowerScan, PtyScan
else:
    from ..utils.verbose import logger
    from ..core.data import PtydScan, MoonFlowerScan, PtyScan

PtyScanTypes = dict(
    i13dls_ffp = I13ScanFFP,
    i13dls_nfp = I13ScanNFP,
    dls = DlsScan,
    i08dls = I08Scan,
    savu = Savu,
    plugin = makeScanPlugin,
    id16a_nfp = ID16AScan,
    amo_lcls = AMOScan,
    diproi_fermi = DiProIFERMIScan,
    fli_spec_multexp = FliSpecScanMultexp,
    laser_ucl = UCLLaserScan,
    nanomaxstepscannov2016 = NanomaxStepscanNov2016,
    nanomaxstepscanmay2017 = NanomaxStepscanMay2017,
    nanomaxflyscanjune2017 = NanomaxFlyscanJune2017,
    als5321 = ALS5321Scan,
)

def makePtyScan(pars, scanmodel=None):
    """
    Factory for PtyScan object. Return an instance of the appropriate PtyScan subclass based on the
    input parameters.

    Parameters
    ----------
    pars: dict or Param
        Input parameters according to :py:data:`.scan.data`.

    scanmodel: ScanModel object
        FIXME: This seems to be needed for simulations but broken for now.
    """

    if __name__ == "__main__":
        from ptypy.experiment import PtyScanTypes
    else:
        from ..experiment import PtyScanTypes

    # Extract information on the type of object to build
    source = pars.source
    recipe = pars.get('recipe', {})

    if source is not None:
        source = source.lower()

    if source in PtyScanTypes:
        ps_obj = PtyScanTypes[source]
        logger.info('Scan will be prepared with the recipe "%s"' % source)
        ps_instance = ps_obj(pars, recipe=recipe)
    elif source.endswith('.ptyd') or source.endswith('.pty') or str(source) == 'file':
        ps_instance = PtydScan(pars, source=source)
    elif source == 'test':
        ps_instance = MoonFlowerScan(pars)
    elif source == 'sim':
        from ..simulations import SimScan
        logger.info('Scan will simulated')
        ps_instance = SimScan(pars, scanmodel)
    elif source == 'empty' or source is None:
        pars.recipe = None
        logger.warning('Generating dummy PtyScan - This label will source only zeros as data')
        ps_instance = PtyScan(pars)
    else:
        raise RuntimeError('Could not manage source "%s"' % str(source))

    return ps_instance
