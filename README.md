# kontex-conan

Local Conan package index for KonteX projects.

## Available Packages

* **libxdaq** C++ interface library for XDAQ hardware
* **libxdaqnp** Neuropixels integration for XDAQ
* **xdaqmetadata** Metadata handling for ThorVision recordings

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
xdaqmetadata/0.1.1
```

## Projects Using This Index

* [XDAQ-OE](https://github.com/kontex-neuro/XDAQ-OE)
* [XDAQ-Neuropixels](https://github.com/kontex-neuro/XDAQ-Neuropixels)
* [pylibxdaq](https://github.com/kontex-neuro/pylibxdaq)
* [Intan-RHX](https://github.com/kontex-neuro/Intan-RHX)
