# kontex-conan

Local Conan package index for KonteX projects.

## Available Packages

* **libxdaq**: C++ interface library for XDAQ hardware
* **libxdaqnp**: Neuropixels integration for XDAQ
* **libxvc**: C++ interface library for ThorVision
* **xdaqmetadata**: Metadata handling for ThorVision recordings

## Usage

```bash
git clone https://github.com/kontex-neuro/kontex-conan.git kontex-conan
conan remote add --force kontex-neuro ./kontex-conan
```

Then reference packages in your `conanfile.txt` or `conanfile.py`:

```
[requires]
libxdaq/0.5.2
libxdaqnp/0.6.1
libxvc/0.3.0
xdaqmetadata/0.2.0
```

## Projects Using This Index

* [XDAQ-OE](https://github.com/kontex-neuro/XDAQ-OE)
* [XDAQ-Neuropixels](https://github.com/kontex-neuro/XDAQ-Neuropixels)
* [pylibxdaq](https://github.com/kontex-neuro/pylibxdaq)
* [Intan-RHX](https://github.com/kontex-neuro/Intan-RHX)
* [ThorVision](https://github.com/kontex-neuro/ThorVision)
