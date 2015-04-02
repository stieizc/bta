bio = {(1 << 1, 'discard'), (1 << 0, 'write'), (1 << 2, 'read'),
       (1 << 3, 'rahead'), (1 << 4, 'barrier'), (1 << 5, 'sync'),
       (1 << 6, 'meta'), (1 << 7, 'secure'), (1 << 8, 'flush'),
       (1 << 9, 'fua')}


def parse_bio(rwbs):
    return parse(rwbs, bio)


qemu_aio = {(1 << 4, 'discard'), (1 << 0, 'read'), (1 << 1, 'write'),
            (1 << 2, 'ioctl'), (1 << 3, 'flush'),  (1 << 5, 'writez')}


def parse_qemu_aio(rwbs):
    return parse(rwbs, qemu_aio)


def parse(rwbs, flags):
    ops = []
    for bit, name in bio.iteritems():
        if (bit & rwbs):
            actions.append(name)
    return ops
