axes_dict = {
    "angle": ["wavenumber", "ifft", "rad"],
    "time": ["freqs", "ifft", "s"],
    "xyz": ["rphiz", "pol2cart", "m"],
}
axes_dict_transformation = axes_dict

rev_axes_dict = {
    "wavenumber": ["angle", "fft", "dimless"],
    "freqs": ["time", "fft", "Hz"],
    "rphiz": ["xyz", "cart2pol", "m"],
}
