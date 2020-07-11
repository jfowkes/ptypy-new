"""
This script is a test for ptychographic reconstruction in the absence
of actual data. It uses the test Scan class
`ptypy.core.data.MoonFlowerScan` to provide "data".
"""
#import ptypy
from ptypy.core import Ptycho
from ptypy import utils as u
#import numpy
#numpy.seterr(divide='raise', invalid='raise')

p = u.Param()

# for verbose output
p.verbose_level = 4

# set home path
p.io = u.Param()
p.io.home = "/tmp/ptypy/"
p.io.autosave = None
p.io.autoplot = u.Param()
p.io.autoplot.active = True

# max 100 frames (128x128px) of diffraction data
p.scans = u.Param()
p.scans.MF = u.Param()
p.scans.MF.name = 'Full'
p.scans.MF.data= u.Param()
p.scans.MF.data.name = 'MoonFlowerScan'
p.scans.MF.data.shape = 128
p.scans.MF.data.num_frames = 200
p.scans.MF.data.save = None

# position distance in fraction of illumination frame
p.scans.MF.data.density = 0.2
# total number of photon in empty beam
p.scans.MF.data.photons = 1e5
# Gaussian FWHM of possible detector blurring
p.scans.MF.data.psf = 0.

# attach a reconstrucion engine
p.engines = u.Param()
p.engines.engine00 = u.Param()
p.engines.engine00.name = 'DM'
p.engines.engine00.numiter = 50
p.engines.engine00.probe_center_tol = 1
p.engines.engine00.probe_support = 0.6
p.engines.engine00.fourier_relax_factor = .2
p.engines.engine00.obj_smooth_std = 20.
p.engines.engine00.object_inertia = 0.1

p.engines.engine01 = u.Param()
p.engines.engine01.name = 'ML'
p.engines.engine01.ML_type = 'Poisson'
p.engines.engine01.reg_del2 = True                      # Whether to use a Gaussian prior (smoothing) regularizer
p.engines.engine01.reg_del2_amplitude = 0.1             # Amplitude of the Gaussian prior if used
p.engines.engine01.scale_precond = True
p.engines.engine01.scale_probe_object = 1.
p.engines.engine01.smooth_gradient = 20.
p.engines.engine01.smooth_gradient_decay = 1/50.
p.engines.engine01.floating_intensities = False
p.engines.engine01.numiter = 300
# prepare and run
P = Ptycho(p, level=5)
