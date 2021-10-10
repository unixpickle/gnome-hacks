def reusable_device_expr(dev_type: str) -> str:
    """
    Create a virtual input device and cache the result for the lifetime of the
    GNOME shell process.

    :param dev_type: a Clutter.InputDeviceType member, like "POINTER_DEVICE"
                     or "KEYBOARD_DEVICE".
    :return: a JavaScript expression to get the device
    """
    res = (
        """(function() {
        const Clutter = imports.gi.Clutter;
        const seat = Clutter.get_default_backend().get_default_seat();
        if (!global._gnomeHacksDevices) {
            global._gnomeHacksDevices = {};
        }
        const key = '"""
        + dev_type
        + """';
        if (global._gnomeHacksDevices[key]) {
            return global._gnomeHacksDevices[key];
        }
        const dev = seat.create_virtual_device(Clutter.InputDeviceType."""
        + dev_type
        + """);
        global._gnomeHacksDevices[key] = dev;
        return dev;
    })()"""
    )
    return "".join([x.strip() for x in res.split("\n")])
