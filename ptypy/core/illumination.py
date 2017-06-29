# -*- coding: utf-8 -*-
"""
This module generates the probe.

@author: Bjoern Enders

This file is part of the PTYPY package.

    :copyright: Copyright 2014 by the PTYPY team, see AUTHORS.
    :license: GPLv2, see LICENSE for details.

"""
import numpy as np

from .. import utils as u
from ..core import geometry
from ..utils.verbose import logger
from .. import resources

TEMPLATES = dict()
from io import StringIO

StringIO(
u"""
[aperture]
help = Beam aperture parameters

[aperture.central_stop]
help = size of central stop as a fraction of aperture.size
default = None
doc = If not None: places a central beam stop in aperture. The value given here is the fraction of the beam stop compared to `size` 
lowlim = 0.
uplim = 1.
userlevel = 1
type = float

[aperture.diffuser]
help = Noise in the transparen part of the aperture
default = None
doc = Can be either:
	 - ``None`` : no noise
	 - ``2-tuple`` : noise in phase (amplitude (rms), minimum feature size)
	 - ``4-tuple`` : noise in phase & modulus (rms, mfs, rms_mod, mfs_mod)
userlevel = 2
type = tuple

[aperture.edge]
help = Edge width of aperture (in pixels!)
default = 2.0
userlevel = 2

[aperture.form]
help = One of None, 'rect' or 'circ'
default = circ
doc = One of:
	 - ``None`` : no aperture, this may be useful for nearfield
	 - ``'rect'`` : rectangular aperture
	 - ``'circ'`` : circular aperture
choices = None,'rect','circ'
userlevel = 2
type = None

[aperture.offset]
help = Offset between center of aperture and optical axes
default = 0.
doc = May also be a tuple (vertical,horizontal) for size in case of an asymmetric offset
userlevel = 2
type = float, tuple

[aperture.size]
lowlim = 0.
help = Aperture width or diameter
default = None
doc = May also be a tuple *(vertical,horizontal)* in case of an asymmetric aperture 
userlevel = 0
type = float

[diversity]
help = Probe mode(s) diversity parameters
doc = Can be ``None`` i.e. no diversity
validity = 
choices = 
uplim = 
userlevel = 
type = Param

[diversity.noise]
lowlim = 
help = Noise in the generated modes of the illumination 
default = None
doc = Can be either:
	 - ``None`` : no noise
	 - ``2-tuple`` : noise in phase (amplitude (rms), minimum feature size)
	 - ``4-tuple`` : noise in phase & modulus (rms, mfs, rms_mod, mfs_mod)
validity = 
choices = 
uplim = 
userlevel = 1
type = tuple

[diversity.power]
lowlim = 0.0
help = Power of modes relative to main mode (zero-layer)
default = 0.1
uplim = 1.0
userlevel = 1
type = tuple, float

[diversity.shift]
help = Lateral shift of modes relative to main mode
default = None
doc = **[not implemented]**
userlevel = 2
type = float

[model] 
help = Type of illumination model
default = None
doc = One of:
	 - ``None`` : model initialitziation defaults to flat array filled with the specified number of photons
	 - ``'recon'`` : load model from previous reconstruction, see `recon` Parameters
	 - ``'stxm'`` : Estimate model from autocorrelation of mean diffraction data
	 - *<resource>* : one of ptypys internal image resource strings
	 - *<template>* : one of the templates inillumination module
	
	In script, you may pass a numpy.ndarray here directly as the model. It is considered as incoming wavefront and will be propagated according to `propagation` with an optional `aperture` applied before.
userlevel = 0
type = str

[photons]
lowlim = 0
help = Number of photons in the incident illumination
default = None
doc = A value specified here will take precedence over calculated statistics from the loaded data.
userlevel = 2
type = int

[propagation]
help = Parameters for propagation after aperture plane
doc = Propagation to focus takes precedence to parallel propagation if `foccused` is not ``None``

[propagation.antialiasing]
help = Antialiasing factor
default = 1
doc = Antialiasing factor used when generating the probe. (numbers larger than 2 or 3 are memory hungry)
	**[Untested]**
userlevel = 2
type = float

[propagation.focussed]
lowlim = 
help = Propagation distance from aperture to focus
default = None
doc = If ``None`` or ``0`` : No focus propagation 
userlevel = 0
type = float

[propagation.parallel]
help = Parallel propagation distance
default = None
doc = If ``None`` or ``0`` : No parallel propagation 
userlevel = 0
type = float

[propagation.spot_size]
lowlim = 0
help = Focal spot diameter
default = None
doc = If not ``None``, this parameter is used to generate the appropriate aperture size instead of :py:data:`size`
validity = foccussed is not None and foccused!=0
userlevel = 1
type = float

[recon]
help = Parameters to load from previous reconstruction
type = Param

[recon.label]
help = Scan label of diffraction that is to be used for probe estimate
default = None
doc = ``None``, own scan label is used
userlevel = 1
type = str

[recon.rfile]
help = Path to a ``.ptyr`` compatible file
default = \*.ptyr
userlevel = 0
type = file
""")

DEFAULT_aperture = u.Param(
    #  Aperture form (str). One of:
    # - None: no aperture, this may be useful for nearfield
    # - 'rect': rectangular aperture
    # - 'circ': circular aperture
    form='circ',
    # Static Noise in the transparent part of the aperture (float).
    # Can act like a diffuser but has no wavelength dependency
    # Can be either:
    # - None : no noise
    # - 2-tuple: noise in phase (amplitude (rms), minimum feature size)
    # - 4-tuple: noise in phase & modulus (rms, mfs, rms_mod, mfs_mod)
    diffuser=None,
    # Aperture width or diameter (float).
    # May also be a tuple (vertical, horizontal) for size
    # in case of an asymmetric aperture
    size=None,
    # Edge width of aperture in pixel to suppress aliasing (int).
    edge=2,
    # Size of central stop as a fraction of aperture.size (float).
    # If not None: places a central beam stop in aperture.
    # The value given here is the fraction of the stop compared to size
    central_stop=None,
    # Offset between center of aperture and optical axes (float).
    # May also be a tuple (vertical, horizontal) for size
    # in case of an asymmetric offset
    offset=0.,
    # Rotate aperture by this value (float).
    rotate=0.,
)
""" Default illumination.aperture parameters.
    See :py:data:`.scan.illumination.aperture` and a short listing below """

DEFAULT_propagation = u.Param(
    # Parameters for propagation after aperture plane
    # Propagation to focus takes precedence to parallel propagation
    # if focused is not None
    # Parallel propagation distance (float).
    # If None or 0 : No parallel propagation
    parallel=None,
    # Propagation distance from aperture to focus (float).
    # If None or 0 : No focus propagation
    focussed=None,
    # Focal spot diameter (float).
    spot_size=None,
    # Antialiasing factor [not implemented] (float).
    # Antialiasing factor used when generating the probe.
    # (numbers larger than 2 or 3 are memory hungry)
    antialiasing=None,
)

DEFAULT_diversity = u.Param(
    # Noise added on top add the end of initialisation (float).
    # Can be either:
    # - None : no noise
    # - 2-tuple: noise in phase (amplitude (rms), minimum feature size)
    # - 4-tuple: noise in phase & modulus (rms, mfs, rms_mod, mfs_mod)
    noise=None,
    shift=None,
    power=1.0,
)

DEFAULT = u.Param(
    override=None,
    # User-defined probe (if type is None) (str).
    # `None`, path to a *.ptyr file or any python evaluable statement
    # yielding a 3d numpy array, If `None` illumination is modeled.
    model=None,
    # Number of photons in the incident illumination (int, float, None).
    photons=None,
    recon=u.Param(
        rfile='*.ptyr',
        ID=None,
        layer=None,
    ),
    stxm=u.Param(
        # Label of the scan of whose diffraction data to initialize stxm.
        # If None, use own scan_label
        label=None,
    ), 
    # Diversity parameters, can be None = no diversity
    diversity=DEFAULT_diversity,
    # Aperture parameters, can be None = no aperture
    aperture=DEFAULT_aperture,
    # Propagation parameters, can be None = no propagation
    propagation=DEFAULT_propagation,
)
""" Default illumination parameters. See :py:data:`.scan.illumination`
    and a short listing below """

__all__ = ['DEFAULT', 'init_storage', 'aperture']


def rectangle(grids, dims=None, ew=2):
    if dims is None:
        dims = (grids.shape[-2] / 2., grids.shape[-1] / 2.)
    v, h = dims
    V, H = grids
    return (u.smooth_step(-np.abs(V) + v/2, ew)
            * u.smooth_step(-np.abs(H) + h/2, ew))


def ellipsis(grids, dims=None, ew=2):
    if dims is None:
        dims = (grids.shape[-2] / 2., grids.shape[-1] / 2.)
    v, h = dims
    V, H = grids
    return u.smooth_step(
        0.5 - np.sqrt(V**2/v**2 + H**2/h**2), ew/np.sqrt(v * h))


def aperture(A, grids=None, pars=None, **kwargs):
    """
    Creates an aperture in the shape and dtype of `A` according 
    to x,y-grids `grids`. Keyword Arguments may be any of 
    :any:`DEFAULT`.aperture.
    
    Parameters
    ----------
    A : ndarray
        Model array (at least 2-dimensional) to place aperture on top.
        
    pars: dict or ptypy.utils.Param
        Parameters, see :any:`DEFAULT`.aperture
        
    grids : ndarray
        Cartesian coordinate grids, if None, they will be created with
        ``grids = u.grids(sh[-2:], psize=(1.0, 1.0))``
        
    Returns
    -------
    ap : ndarray
        Aperture array (complex) in shape of A
    """
    p = u.Param(DEFAULT_aperture.copy())
    if pars is not None:
        p.update(pars)
        p.update(**kwargs)
    
    sh = A.shape
    if grids is not None:
        grids = np.array(grids).copy()
        psize = np.array((grids[0, 1, 0] - grids[0, 0, 0],
                          grids[1, 0, 1] - grids[1, 0, 0]))
        assert ((np.array(grids.shape[-2:]) - np.array(sh[-2:])) == 0).any(), (
            'Grid and Input dimensions do not match')
    else:
        psize = u.expect2(1.0)
        grids = u.grids(sh[-2:], psize=psize)
        
    ap = np.ones(sh[-2:], dtype=A.dtype)

    if p.diffuser is not None:
        ap *= u.parallel.MPInoise2d(sh[-2:], *p.diffuser)
        
    if p.form is not None:
        off = u.expect2(p.offset)
        cgrid = grids[0].astype(complex) + 1j*grids[1]
        cgrid -= np.complex(off[0], off[1])
        cgrid *= np.exp(1j * p.rotate)
        grids[0] = cgrid.real / psize[0]
        grids[1] = cgrid.imag / psize[1]

        if str(p.form) == 'circ':
            apert = lambda x: ellipsis(grids, x, p.edge)
        elif str(p.form) == 'rect':
            apert = lambda x: rectangle(grids, x, p.edge)
        else:
            raise NotImplementedError(
                'Only elliptical `circ` or rectangular `rect` apertures are'
                'supported for now.')

        if p.size is not None:
            dims = u.expect2(p.size) / psize
        else:
            dims = np.array(cgrid.shape) / 3.

        ap *= apert(dims)
        if p.central_stop is not None:
            dims *= u.expect2(p.central_stop)
            ap *= 1 - apert(dims)

    return np.resize(ap, sh)


def init_storage(storage, pars, energy=None, **kwargs):
    """
    Initializes :any:`Storage` `storage` with parameters from `pars`
    
    Parameters
    ----------
    storage : ptypy.core.Storage
        A :any:`Storage` instance in the *probe* container of :any:`Ptycho`
        
    pars : Param
        Parameter structure for creating a probe / illumination. 
        See :any:`DEFAULT`
        Also accepted as argument:
         * string giving the filename of a previous reconstruction to
           extract storage from.
         * string giving the name of an available TEMPLATE
         * FIXME: document other string cases.
         * numpy array: interpreted as initial illumination.
        
    energy : float, optional
        Energy associated with this storage. If None, tries to retrieve
        the energy from the already initialized ptypy network. 
    """
    s = storage
    prefix = "[Object %s] " % str(s.ID)
    
    p = DEFAULT.copy(depth=3)
    model = None
    if hasattr(pars, 'items') or hasattr(pars, 'iteritems'):
        # This is a dict
        p.update(pars, in_place_depth=3)    
    
    # First we check for scripting shortcuts. This is only convenience.
    elif str(pars) == pars:
        # This maybe a template now or a file
        
        # Deactivate further processing
        p.aperture = None
        p.propagation = None
        p.diversity = None
        
        if pars.endswith('.ptyr'):
            recon = u.Param(rfile=pars, layer=None, ID=s.ID)
            p.recon = recon
            p.model = 'recon'
            try:
                init_storage(s, p, energy=1.0)
            except KeyError:
                logger.warning(
                    prefix +
                    'Loading of probe storage `%s` failed. Trying any storage.'
                    % s.ID)
                p.recon.ID = None
                init_storage(s, p, energy=1.0)
            return
        elif pars in TEMPLATES.keys():
            init_storage(s, TEMPLATES[pars])
            return 
        elif pars in resources.probes or pars == 'stxm':
            p.model = pars
            init_storage(s, p)
            return
        else:
            raise RuntimeError(
                prefix +
                'Shortcut string `%s` for probe creation is not understood.'
                % pars)
    elif type(pars) is np.ndarray:
        p.model = pars
        p.aperture = None
        p.propagation = None
        p.diversity = None
        init_storage(s, p)
        return
    else:
        ValueError(prefix + 'Shortcut for probe creation is not understood.')
        
    if p.model is None:
        model = np.ones(s.shape, s.dtype)
        if p.photons is not None:
            model *= np.sqrt(p.photons) / np.prod(s.shape)
    elif type(p.model) is np.ndarray:
        model = p.model
    elif p.model in resources.probes:
        model = resources.probes[p.model](s.shape)
    elif str(p.model) == 'recon':
        # Loading from a reconstruction file
        layer = p.recon.get('layer')
        ID = p.recon.get('ID')
        logger.info(
            prefix +
            'Attempt to load layer `%s` of probe storage with ID `%s` from `%s`'
            % (str(layer), str(ID), p.recon.rfile))
        model = u.load_from_ptyr(p.recon.rfile, 'probe', ID, layer)
        # This could be more sophisticated,
        # i.e. matching the real space grids etc.
    elif str(p.model) == 'stxm':
        logger.info(
            prefix + 'Probe initialization using averaged diffraction data.')
        # Pick a pod that no matter if active or not
        pod = s.views[0].pod

        # Accumulate intensities
        alldiff = np.zeros(pod.geometry.shape)
        n = np.array(0, dtype=int)
        for v in s.views:
            if not v.pod.active:
                continue
            alldiff += v.pod.diff
            n += 1
        # Communicate result
        u.parallel.allreduce(alldiff)
        u.parallel.allreduce(n)
        # Compute mean
        if n > 0:
            alldiff /= n

        # Pick a propagator and a pod
        # In far field we will have to know the wavefront curvature
        try:
            curve = pod.geometry.propagator.post_curve
        except:
            # Ok this is nearfield
            curve = 1.0 
            
        model = pod.bw(curve * np.sqrt(alldiff))
    else:
        raise ValueError(
            prefix + 'Value to `model` key not understood in probe creation')
        
    assert type(model) is np.ndarray, "".join(
        [prefix, "Internal model should be numpy array now but it is %s."
         % str(type(model))])

    # Expand model to the right length filling with copies
    sh = model.shape[-2:]
    model = np.resize(model, (s.shape[0], sh[0], sh[1]))

    # Find out about energy if not set
    if energy is None:
        try:
            energy = s.views[0].pod.geometry.energy
        except:
            logger.info(prefix +
                        'Could not retrieve energy from pod network... '
                        'Maybe there are no pods yet created?')
    s._energy = energy
        
    # Perform aperture multiplication, propagation etc.
    model = _process(model, p.aperture, p.propagation,
                     p.photons, energy, s.psize, prefix)
    
    # Apply diversity
    if p.diversity is not None:
        u.diversify(model, **p.diversity)
    
    # Fill storage array
    s.fill(model)


def _process(model, aperture_pars=None, prop_pars=None, photons=1e7,
             energy=6., resolution=7e-8, prefix="", **kwargs):
    """
    Processes 3d stack of incoming wavefronts `model`. Applies aperture
    according to `aperture_pars` and propagates according to `prop_pars`
    and other keywords arguments. 
    """
    # Create the propagator
    ap_size, grids, prop = _propagation(prop_pars,
                                        model.shape[-2:],
                                        resolution,
                                        energy,
                                        prefix)
        
    # Form the aperture on top of the model
    if type(aperture_pars) is np.ndarray:
        model *= np.resize(aperture_pars, model.shape)
    elif aperture_pars is not None:
        if ap_size is not None:
            aperture_pars.size = ap_size
        model *= aperture(model, grids, aperture_pars)
    else:
        logger.warning(
            prefix +
            'No aperture defined in probe creation. This may lead to artifacts '
            'if the probe model is not chosen carefully.')

    # Propagate
    model = prop(model)
    
    # apply photon count
    if photons is not None:
        model *= np.sqrt(photons / u.norm2(model))
    
    return model


def _propagation(prop_pars, shape=None, resolution=None, energy=None,
                 prefix=""):
    """
    Helper function for the propagation of the model illumination (in _process).
    :param prop_pars: propagation parameters
    :param shape:
    :param resolution:
    :param energy:
    :return:
    """
    p = prop_pars
    grids = None
    if p is not None and len(p) > 0:
        ap_size = p.spot_size if p.spot_size is not None else None 
        ffGeo = None
        nfGeo = None
        fdist = p.focussed
        if fdist is not None:
            geodct = u.Param(
                energy=energy,
                shape=shape,
                psize=resolution,
                resolution=None,
                distance=fdist,
                propagation='farfield'
                )
            ffGeo = geometry.Geo(pars=geodct)
            # ffGeo._initialize(geodct)

            if p.spot_size is not None:
                ap_size = (ffGeo.lam * fdist / np.array(p.spot_size)
                           * 2 * np.sqrt(np.sqrt(2)))
            else:
                ap_size = None
            grids = ffGeo.propagator.grids_sam
            phase = np.exp(
                -1j * np.pi / ffGeo.lam / fdist * (grids[0]**2 + grids[1]**2))
            logger.info(
                prefix +
                'Model illumination is focussed over a distance %3.3g m.'
                % fdist)
            # from matplotlib import pyplot as plt
            # plt.figure(100); plt.imshow(u.imsave(ffGeo.propagator.post_fft))
        if p.parallel is not None:
            geodct = u.Param(
                energy=energy,
                shape=shape,
                resolution=resolution,
                psize=None,
                distance=p.parallel,
                propagation='nearfield'
                )
            nfGeo = geometry.Geo(pars=geodct)
            # nfGeo._initialize(geodct)
            grids = nfGeo.propagator.grids_sam if grids is None else grids
            logger.info(
                prefix +
                'Model illumination is propagated over a distance %3.3g m.'
                % p.parallel)
            
        if ffGeo is not None and nfGeo is not None:
            prop = lambda x: nfGeo.propagator.fw(ffGeo.propagator.fw(x * phase))
        elif ffGeo is not None and nfGeo is None:
            prop = lambda x: ffGeo.propagator.fw(x * phase)
        elif ffGeo is None and nfGeo is not None:
            prop = lambda x: nfGeo.propagator.fw(x)
        else:
            grids = u.grids(u.expect2(shape), psize=u.expect2(resolution))
            prop = lambda x: x
    else:
        grids = u.grids(u.expect2(shape), psize=u.expect2(resolution))
        prop = lambda x: x
        ap_size = None
        
    return ap_size, grids, prop

DEFAULT_old = u.Param(
    # 'focus','parallel','path_to_file'
    probe_type='parallel',
    # 'rect','circ','path_to_file'
    aperture_type='circ',
    # aperture diameter
    aperture_size=None,
    # edge smoothing width of aperture in pixel
    aperture_edge=1,
    # distance from prefocus aperture to focus
    focal_dist=None,
    # propagation distance from focus (or from aperture if parallel)
    prop_dist=0.001,
    # use the conjugate of the probe instead of the probe
    UseConjugate=False,
    # antialiasing factor used when generating the probe
    antialiasing=2.0,
    # if aperture_size = None this parameter is used instead.
    # Gives the desired probe size in sample plane
    # if spot_size = None, a 50 pixel aperture will be used
    spot_size=None,
    # incoming
    incoming=None,
    probe=None,
    # photons in the probe
    photons=1e8,
    mode_diversity='noise',
    # first weight is main mode, last weight will be copied if
    # more modes requested than weight given
    mode_weights=[1., 0.1],
    # energy spectrum of source, choose None, 'Gauss' or 'Box'
    spectrum=None,
    # bandwidth of source
    bandwidth=0.1,
    phase_noise_rms=None,
    phase_noise_mfs=0.0,
)


if __name__ == '__main__':
    energy = 6.
    shape = 512
    resolution = 8e-8
    p = u.Param()
    p.aperture = u.Param()
    p.aperture.form = 'circ'
    p.aperture.diffuser = (10.0, 5, 0.1, 20.0)
    p.aperture.size = 100e-6
    # (int) Edge width of aperture in pixel to suppress aliasing
    p.aperture.edge = 2
    p.aperture.central_stop = 0.3
    p.aperture.offset = 0.
    # (float) rotate aperture by this value
    p.aperture.rotate = 0.
    # Parameters for propagation after aperture plane
    p.propagation = u.Param()
    # (float) Parallel propagation distance
    p.propagation.parallel = 0.015
    # (float) Propagation distance from aperture to focus
    p.propagation.focussed = 0.1
    # (float) Focal spot diameter
    p.propagation.spot_size = None
    # (float) antialiasing factor
    p.propagation.antialiasing = None
    # (str) User-defined probe (if type is None)
    p.probe = None
    # (int, float, None) Number of photons in the incident illumination
    p.photons = None
    # (float) Noise added on top add the end of initialisation
    p.noise = None

    probe = from_pars_no_storage(pars=p,
                                 energy=energy,
                                 shape=shape,
                                 resolution=resolution)

    from matplotlib import pyplot as plt
    plt.imshow(u.imsave(abs(probe[0])))
