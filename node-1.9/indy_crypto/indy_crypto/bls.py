import logging
from ctypes import POINTER, c_void_p, byref, c_size_t, c_ubyte, c_bool
from .lib import do_call


class BlsEntity:
    """
    Base class for BLS Entities (Generator, SignKey, VerKey, Signature, MultiSignature).
    """
    new_handler = None
    from_bytes_handler = None
    as_bytes_handler = None
    free_handler = None

    def __init__(self, c_instance):
        logger = logging.getLogger(__name__)
        logger.debug("BlsEntity.__init__: >>> self: %r, instance: %r", self, c_instance)

        self.c_instance = c_instance

    @classmethod
    def from_bytes(cls, xbytes):
        """
        Creates and Bls entity from bytes representation.
        :param xbytes: Bytes representation of Bls entity
        :return: BLS entity intance
        """
        logger = logging.getLogger(__name__)
        logger.debug("BlsEntity::from_bytes: >>>")

        c_instance = c_void_p()
        do_call(cls.from_bytes_handler, xbytes, len(xbytes), byref(c_instance))

        res = cls(c_instance)

        logger.debug("BlsEntity::from_bytes: <<< res: %r", res)
        return res

    def as_bytes(self):
        """
        Returns BLS entity bytes representation.
        :return: BLS entity bytes representation
        """
        logger = logging.getLogger(__name__)
        logger.debug("BlsEntity.as_bytes: >>> self: %r", self)

        xbytes = POINTER(c_ubyte)()
        xbytes_len = c_size_t()

        do_call(self.as_bytes_handler, self.c_instance, byref(xbytes), byref(xbytes_len))
        res = bytes(xbytes[:xbytes_len.value])

        logger.debug("BlsEntity.as_bytes: <<< res: %r", res)
        return res

    def __del__(self):
        logger = logging.getLogger(__name__)
        logger.debug("BlsEntity.__del__: >>> self: %r", self)

        do_call(self.free_handler, self.c_instance)


class Generator(BlsEntity):
    """
    BLS generator point.
    BLS algorithm requires choosing of generator point that must be known to all parties.
    The most of BLS methods require generator to be provided.
    """
    new_handler = 'ursa_bls_generator_new'
    from_bytes_handler = 'ursa_bls_generator_from_bytes'
    as_bytes_handler = 'ursa_bls_generator_as_bytes'
    free_handler = 'ursa_bls_generator_free'

    @classmethod
    def new(cls):
        """
        Creates and returns random generator point that satisfy BLS algorithm requirements.
        :return: BLS generator
        """
        logger = logging.getLogger(__name__)
        logger.debug("Generator::new: >>>")

        c_instance = c_void_p()
        do_call(cls.new_handler, byref(c_instance))

        res = cls(c_instance)

        logger.debug("Generator::new: <<< res: %r", res)
        return res


class SignKey(BlsEntity):
    """
    BLS sign key.
    """
    new_handler = 'ursa_bls_sign_key_new'
    from_bytes_handler = 'ursa_bls_sign_key_from_bytes'
    as_bytes_handler = 'ursa_bls_sign_key_as_bytes'
    free_handler = 'ursa_bls_sign_key_free'

    @classmethod
    def new(cls, seed):
        """
        Creates and returns random (or seeded from seed) BLS sign key.
        :param: seed - Optional seed.
        :return: BLS sign key
        """
        logger = logging.getLogger(__name__)
        logger.debug("SignKey::new: >>>")

        c_instance = c_void_p()
        do_call(cls.new_handler, seed, len(seed) if seed is not None else 0, byref(c_instance))

        res = cls(c_instance)

        logger.debug("SignKey::new: <<< res: %r", res)
        return res


class VerKey(BlsEntity):
    """
    BLS verification key.
    """
    new_handler = 'ursa_bls_ver_key_new'
    from_bytes_handler = 'ursa_bls_ver_key_from_bytes'
    as_bytes_handler = 'ursa_bls_ver_key_as_bytes'
    free_handler = 'ursa_bls_ver_key_free'

    @classmethod
    def new(cls, gen, sign_key):
        """
        Creates and returns BLS ver key that corresponds to the given generator and sign key.
        :param: gen - Generator
        :param: sign_key - Sign Key
        :return: BLS verification key
        """
        logger = logging.getLogger(__name__)
        logger.debug("VerKey::new: >>>")

        c_instance = c_void_p()
        do_call(cls.new_handler, gen.c_instance, sign_key.c_instance, byref(c_instance))

        res = cls(c_instance)

        logger.debug("VerKey::new: <<< res: %r", res)
        return res


class ProofOfPossession(BlsEntity):
    """
    BLS proof of possession.
    """
    new_handler = 'ursa_bls_pop_new'
    from_bytes_handler = 'ursa_bls_pop_from_bytes'
    as_bytes_handler = 'ursa_bls_pop_as_bytes'
    free_handler = 'ursa_bls_pop_free'

    @classmethod
    def new(cls, ver_key, sign_key):
        """
        Creates and returns BLS proof of possession that corresponds to the given ver key and sign key.
        :param: ver_key - Ver Key
        :param: sign_key - Sign Key
        :return: BLS proof of possession
        """
        logger = logging.getLogger(__name__)
        logger.debug("ProofOfPossession::new: >>>")

        c_instance = c_void_p()
        do_call(cls.new_handler, ver_key.c_instance, sign_key.c_instance, byref(c_instance))

        res = cls(c_instance)

        logger.debug("ProofOfPossession::new: <<< res: %r", res)
        return res


class Signature(BlsEntity):
    """
    BLS signature.
    """
    new_handler = None
    from_bytes_handler = 'ursa_bls_signature_from_bytes'
    as_bytes_handler = 'ursa_bls_signature_as_bytes'
    free_handler = 'ursa_bls_signature_free'


class MultiSignature(BlsEntity):
    """
    BLS multi signature.
    """
    new_handler = 'ursa_bls_multi_signature_new'
    from_bytes_handler = 'ursa_bls_multi_signature_from_bytes'
    as_bytes_handler = 'ursa_bls_multi_signature_as_bytes'
    free_handler = 'ursa_bls_multi_signature_free'

    @classmethod
    def new(cls, signatures):
        """
        Creates and returns BLS multi signature that corresponds to the given signatures list.
        :param: signature - List of signatures
        :return: BLS multi signature
        """
        logger = logging.getLogger(__name__)
        logger.debug("MultiSignature::new: >>>")

        # noinspection PyCallingNonCallable,PyTypeChecker
        signature_c_instances = (c_void_p * len(signatures))()
        for i in range(len(signatures)):
            signature_c_instances[i] = signatures[i].c_instance

        c_instance = c_void_p()
        do_call(cls.new_handler, signature_c_instances, len(signatures), byref(c_instance))

        res = cls(c_instance)

        logger.debug("MultiSignature::new: <<< res: %r", res)
        return res


class Bls:
    """
    Provides Bls methods.
    """

    @staticmethod
    def sign(message, sign_key):
        """
        Signs the message and returns signature.
        :param: message - Message to sign
        :param: sign_key - Sign key
        :return: Signature
        """

        logger = logging.getLogger(__name__)
        logger.debug("Bls::sign: >>> message: %r, sign_key: %r", message, sign_key)

        c_instance = c_void_p()
        do_call('ursa_bls_sign',
                message, len(message),
                sign_key.c_instance,
                byref(c_instance))

        res = Signature(c_instance)

        logger.debug("Bls::sign: <<< res: %r", res)
        return res

    @staticmethod
    def verify(signature, message, ver_key, gen):
        """
        Verifies the message signature and returns true - if signature valid or false otherwise.
        :param: signature - Signature to verify
        :param: message - Message to verify
        :param: ver_key - Verification key
        :param: gen - Generator point
        :return: true if signature valid
        """

        logger = logging.getLogger(__name__)
        logger.debug("Bls::verify: >>> signature: %r, message: %r, ver_key: %r, gen: %r", signature, message, ver_key,
                     gen)

        valid = c_bool()
        do_call('ursa_bls_verify',
                signature.c_instance,
                message, len(message),
                ver_key.c_instance,
                gen.c_instance,
                byref(valid))

        res = valid
        logger.debug("Bls::verify: <<< res: %r", res)
        return res

    @staticmethod
    def verify_pop(pop, ver_key, gen):
        """
        Verifies the proof of possession and returns true - if signature valid or false otherwise.
        :param: pop - Proof of possession
        :param: ver_key - Verification key
        :param: gen - Generator point
        :return: true if signature valid
        """

        logger = logging.getLogger(__name__)
        logger.debug("Bls::verify_pop: >>> pop: %r, ver_key: %r, gen: %r",
                     pop,
                     ver_key,
                     gen)

        valid = c_bool()
        do_call('ursa_bls_verify_pop',
                pop.c_instance,
                ver_key.c_instance,
                gen.c_instance,
                byref(valid))

        res = valid
        logger.debug("Bls::verify_pop: <<< res: %r", res)
        return res

    @staticmethod
    def verify_multi_sig(multi_sig, message, ver_keys, gen):
        """
        Verifies the message multi signature and returns true - if signature valid or false otherwise.
        :param: multi_sig - Multi signature to verify
        :param: message - Message to verify
        :param: ver_keys - List of verification keys
        :param: gen - Generator point
        :return: true if multi signature valid.
        """

        logger = logging.getLogger(__name__)
        logger.debug("Bls::verify_multi_sig: >>> multi_sig: %r, message: %r, ver_keys: %r, gen: %r",
                     multi_sig, message, ver_keys, gen)

        # noinspection PyCallingNonCallable,PyTypeChecker
        ver_key_c_instances = (c_void_p * len(ver_keys))()
        for i in range(len(ver_keys)):
            ver_key_c_instances[i] = ver_keys[i].c_instance

        valid = c_bool()
        do_call('ursa_bls_verify_multi_sig',
                multi_sig.c_instance,
                message, len(message),
                ver_key_c_instances, len(ver_keys),
                gen.c_instance,
                byref(valid))

        res = valid

        logger.debug("Bls::verify_multi_sig: <<< res: %r", res)
        return res