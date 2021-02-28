'''
Testing on real data
'''

import h5py
import unittest
import numpy as np
from .. import perfrun, PyCudaTest, have_pycuda


if have_pycuda():
    from pycuda import gpuarray
    from ptypy.accelerate.cuda_pycuda.kernels import GradientDescentKernel
from ptypy.accelerate.base.kernels import GradientDescentKernel as BaseGradientDescentKernel

COMPLEX_TYPE = np.complex64
FLOAT_TYPE = np.float32
INT_TYPE = np.int32


class DlsGradientDescentKernelTest(PyCudaTest):

    datadir = "/dls/science/users/iat69393/gpu-hackathon/test-data/"
    iter = 0
    rtol = 1e-6
    atol = 1e-6

    def test_make_model_UNITY(self):

        # Load data
        with h5py.File(self.datadir + "make_model_%04d.h5" %self.iter, "r") as f:
            aux = f["aux"][:]
            addr = f["addr"][:]

        # Copy data to device
        aux_dev = gpuarray.to_gpu(aux)
        addr_dev = gpuarray.to_gpu(addr)

        # CPU Kernel
        BGDK = BaseGradientDescentKernel(aux, addr.shape[1])
        BGDK.allocate()
        BGDK.make_model(aux, addr)

        # GPU kernel
        GDK = GradientDescentKernel(aux_dev, addr.shape[1])
        GDK.allocate()
        GDK.make_model(aux_dev, addr_dev)

        ## Assert
        np.testing.assert_allclose(BGDK.cpu.Imodel, GDK.gpu.Imodel.get(), atol=self.atol, rtol=self.rtol,
            err_msg="`Imodel` buffer has not been updated as expected")


    def test_floating_intensity_UNITY(self):

        # Load data
        with h5py.File(self.datadir + "floating_intensities_%04d.h5" %self.iter, "r") as f:
            w = f["w"][:]
            addr = f["addr"][:]
            I = f["I"][:]
            fic = f["fic"][:]
        with h5py.File(self.datadir + "make_model_%04d.h5" %self.iter, "r") as f:
            aux = f["aux"][:]
        
        # Copy data to device
        aux_dev = gpuarray.to_gpu(aux)
        w_dev = gpuarray.to_gpu(w)
        addr_dev = gpuarray.to_gpu(addr)
        I_dev = gpuarray.to_gpu(I)
        fic_dev = gpuarray.to_gpu(fic)

        # CPU Kernel
        BGDK = BaseGradientDescentKernel(aux, addr.shape[1])
        BGDK.allocate()
        BGDK.floating_intensity(addr, w, I, fic)

        # GPU kernel
        GDK = GradientDescentKernel(aux_dev, addr.shape[1])
        GDK.allocate()
        GDK.floating_intensity(addr_dev, w_dev, I_dev, fic_dev)

        ## Assert
        np.testing.assert_allclose(BGDK.cpu.Imodel, GDK.gpu.Imodel.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="`Imodel` buffer has not been updated as expected")
        np.testing.assert_allcolse(fic, fic_dev.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="floating intensity coeff (fic) has not been updated as expected")


    def test_main_and_error_reduce_UNITY(self):

        # Load data
        with h5py.File(self.datadir + "main_%04d.h5" %self.iter, "r") as f:
            aux = f["aux"][:]
            addr = f["addr"][:]
            w = f["w"][:]
            I = f["I"][:]
        # Load data
        with h5py.File(self.datadir + "error_reduce_%04d.h5" %self.iter, "r") as f:
            err_phot = f["err_phot"][:]

        # Copy data to device
        aux_dev = gpuarray.to_gpu(aux)
        w_dev = gpuarray.to_gpu(w)
        addr_dev = gpuarray.to_gpu(addr)
        I_dev = gpuarray.to_gpu(I)
        err_phot_dev = gpuarray.to_gpu(err_phot)

        # CPU Kernel
        BGDK = BaseGradientDescentKernel(aux, addr.shape[1])
        BGDK.allocate()
        BGDK.main(aux, addr, w, I)
        BGDK.error_reduce(addr, err_phot)

        # GPU kernel
        GDK = GradientDescentKernel(aux_dev, addr.shape[1])
        GDK.allocate()
        GDK.main(aux_dev, addr_dev, w_dev, I_dev)
        GDK.error_reduce(addr_dev, err_phot_dev)

        ## Assert
        np.testing.assert_allclose(aux, aux_dev.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="Auxiliary has not been updated as expected")
        np.testing.assert_allclose(BGDK.cpu.LLerr, GDK.gpu.LLerr.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="LogLikelihood error has not been updated as expected")
        np.testing.assert_array_allclose(err_phot, err_phot_dev.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="`err_phot` has not been updated as expected")


    def test_make_a012_UNITY(self):

        # Load data
        with h5py.File(self.datadir + "make_a012_%04d.h5" %self.iter, "r") as g:
            addr = g["addr"][:]
            I = g["I"][:]
            f = g["f"][:]
            a = g["a"][:]
            b = g["b"][:]
            fic = g["fic"][:]
        with h5py.File(self.datadir + "make_model_%04d.h5" %self.iter, "r") as h:
            aux = h["aux"][:]

        # Copy data to device
        aux_dev = gpuarray.to_gpu(aux)
        addr_dev = gpuarray.to_gpu(addr)
        I_dev = gpuarray.to_gpu(I)
        f_dev = gpuarray.to_gpu(f)
        a_dev = gpuarray.to_gpu(a)
        b_dev = gpuarray.to_gpu(b)
        fic_dev = gpuarray.to_gpu(fic)

        # CPU Kernel
        BGDK = BaseGradientDescentKernel(aux, addr.shape[1])
        BGDK.allocate()
        BGDK.make_a012(f, a, b, addr, I, fic)

        # GPU kernel
        GDK = GradientDescentKernel(aux_dev, addr.shape[1])
        GDK.allocate()
        GDK.make_a012(f_dev, a_dev, b_dev, addr_dev, I_dev, fic_dev)

        ## Assert
        np.testing.assert_allclose(BGDK.cpu.Imodel, GDK.gpu.Imodel.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="Imodel error has not been updated as expected")
        np.testing.assert_allclose(BGDK.cpu.LLerr, GDK.gpu.LLerr.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="LLerr error has not been updated as expected")
        np.testing.assert_allclose(BGDK.cpu.LLden, GDK.gpu.LLden.get(), atol=self.atol, rtol=self.rtol, 
            err_msg="LLden error has not been updated as expected")


    def test_fill_b_UNITY(self):

        # Load data
        with h5py.File(self.datadir + "fill_b_%04d.h5" %self.iter, "r") as f:
            w = f["w"][:]
            addr = f["addr"][:]
            B = f["B"][:]
            Brenorm = f["Brenorm"][...]
        with h5py.File(self.datadir + "make_model_%04d.h5" %self.iter, "r") as f:
            aux = f["aux"][:]
        print(B)

        # Copy data to device
        aux_dev = gpuarray.to_gpu(aux)
        w_dev = gpuarray.to_gpu(w)
        addr_dev = gpuarray.to_gpu(addr)
        B_dev = gpuarray.to_gpu(B.astype(np.float32))

        # CPU Kernel
        BGDK = BaseGradientDescentKernel(aux, addr.shape[1])
        BGDK.allocate()
        BGDK.fill_b(addr, Brenorm, w, B)

        # GPU kernel
        GDK = GradientDescentKernel(aux_dev, addr.shape[1])
        GDK.allocate()
        GDK.fill_b(addr_dev, Brenorm, w_dev, B_dev)

        ## Assert
        np.testing.assert_allclose(B, B_dev.get(), rtol=self.rtol, atol=self.atol, 
            err_msg="`B` has not been updated as expected")

