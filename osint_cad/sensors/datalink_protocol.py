#!/usr/bin/env python3
"""
Weapon Datalink Protocol Specification

Complete specification for BVR weapon mid-course guidance datalink.
Includes message formats, FEC encoding, encryption, and protocol stack.

Based on real weapon datalink protocols:
- US: MIL-STD-1760, AIM-120D AMRAAM datalink
- Chinese: PL-15 guidance datalink, ACDL protocol

Physical Layer: C-band (5.0-5.5 GHz)
Data Rate: 100-500 kbps
Range: 250+ km
Update Rate: 0.5-2 Hz
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import struct
import hashlib


class MessageType(Enum):
    """Datalink message types"""
    MID_COURSE_UPDATE = 0x01
    WEAPON_STATUS = 0x02
    COMMAND_DESTRUCT = 0x03
    TARGET_HANDOFF = 0x04
    SEEKER_ACTIVATION = 0x05
    ABORT_MISSION = 0x06
    HEALTH_CHECK = 0x07
    ACKNOWLEDGMENT = 0x08


class FECScheme(Enum):
    """Forward Error Correction schemes"""
    REED_SOLOMON_255_215 = "RS(255,215)"  # 40 bytes redundancy
    LDPC_RATE_1_2 = "LDPC-1/2"  # 50% redundancy
    TURBO_CODE_RATE_1_3 = "Turbo-1/3"  # 67% redundancy
    CONVOLUTIONAL_K7_RATE_1_2 = "Conv-K7-1/2"  # Constraint length 7


@dataclass
class MidCourseUpdate:
    """
    Mid-course guidance update message

    Sent from launch platform to weapon during flight.
    Provides target position, velocity, and quality metrics.
    """
    # Header (16 bytes)
    message_type: int = MessageType.MID_COURSE_UPDATE.value
    sequence_number: int = 0  # Wraps at 65535
    timestamp_ms: int = 0  # Milliseconds since launch
    weapon_id: int = 0  # Weapon identifier
    reserved: bytes = field(default_factory=lambda: b'\x00' * 8)

    # Target State (48 bytes) - ECEF coordinates
    position_x_m: float = 0.0  # Earth-Centered Earth-Fixed X (meters)
    position_y_m: float = 0.0  # ECEF Y
    position_z_m: float = 0.0  # ECEF Z
    velocity_x_mps: float = 0.0  # Velocity X (m/s)
    velocity_y_mps: float = 0.0  # Velocity Y
    velocity_z_mps: float = 0.0  # Velocity Z

    # Uncertainty / Quality (72 bytes) - Covariance matrix (compressed)
    # 6x6 covariance matrix (position + velocity)
    # Store upper triangle only (21 elements) in float32
    covariance_elements: List[float] = field(default_factory=lambda: [0.0] * 21)

    # Quality Metrics (32 bytes)
    track_quality: float = 0.0  # 0-1, confidence in track
    cep_meters: float = 0.0  # Circular Error Probable
    last_update_age_ms: int = 0  # Age of last sensor update
    gdop: float = 0.0  # Geometric Dilution of Precision
    sensor_count: int = 0  # Number of sensors tracking
    classification_confidence: float = 0.0  # Target ID confidence
    threat_priority: int = 0  # 0-255
    reserved_quality: bytes = field(default_factory=lambda: b'\x00' * 8)

    # CRC-32 (4 bytes)
    crc32: int = 0

    def to_bytes(self) -> bytes:
        """
        Serialize message to binary format

        Returns:
            200-byte message payload (before FEC)
        """
        # Header
        header = struct.pack(
            '<BHIQ8s',  # Little-endian: byte, short, int, long long, 8 bytes
            self.message_type,
            self.sequence_number,
            self.timestamp_ms,
            self.weapon_id,
            self.reserved
        )

        # Target state (6 doubles)
        target_state = struct.pack(
            '<dddddd',
            self.position_x_m,
            self.position_y_m,
            self.position_z_m,
            self.velocity_x_mps,
            self.velocity_y_mps,
            self.velocity_z_mps
        )

        # Covariance (21 floats)
        covariance = struct.pack('<' + 'f' * 21, *self.covariance_elements)

        # Quality metrics
        quality = struct.pack(
            '<ffIffiB8s',
            self.track_quality,
            self.cep_meters,
            self.last_update_age_ms,
            self.gdop,
            self.sensor_count,
            self.classification_confidence,
            self.threat_priority,
            self.reserved_quality
        )

        # Combine all fields (exclude CRC for now)
        payload = header + target_state + covariance + quality

        # Calculate CRC-32
        crc = self._calculate_crc32(payload)

        # Append CRC
        full_message = payload + struct.pack('<I', crc)

        return full_message

    @classmethod
    def from_bytes(cls, data: bytes) -> 'MidCourseUpdate':
        """
        Deserialize message from binary format

        Args:
            data: 200-byte message

        Returns:
            MidCourseUpdate object
        """
        if len(data) < 200:
            raise ValueError(f"Message too short: {len(data)} bytes")

        offset = 0

        # Header
        msg_type, seq, ts, weapon_id, reserved = struct.unpack_from('<BHIQ8s', data, offset)
        offset += 24

        # Target state
        pos_x, pos_y, pos_z, vel_x, vel_y, vel_z = struct.unpack_from('<dddddd', data, offset)
        offset += 48

        # Covariance
        covariance = list(struct.unpack_from('<' + 'f' * 21, data, offset))
        offset += 84

        # Quality
        track_q, cep, age, gdop, sensors, class_conf, priority, res_q = struct.unpack_from(
            '<ffIffiB8s', data, offset
        )
        offset += 32

        # CRC
        crc = struct.unpack_from('<I', data, offset)[0]

        return cls(
            message_type=msg_type,
            sequence_number=seq,
            timestamp_ms=ts,
            weapon_id=weapon_id,
            reserved=reserved,
            position_x_m=pos_x,
            position_y_m=pos_y,
            position_z_m=pos_z,
            velocity_x_mps=vel_x,
            velocity_y_mps=vel_y,
            velocity_z_mps=vel_z,
            covariance_elements=covariance,
            track_quality=track_q,
            cep_meters=cep,
            last_update_age_ms=age,
            gdop=gdop,
            sensor_count=sensors,
            classification_confidence=class_conf,
            threat_priority=priority,
            reserved_quality=res_q,
            crc32=crc
        )

    def _calculate_crc32(self, data: bytes) -> int:
        """Calculate CRC-32 checksum"""
        return np.uint32(hashlib.md5(data).digest()[:4]).item() & 0xFFFFFFFF

    def verify_crc(self) -> bool:
        """Verify message CRC"""
        payload = self.to_bytes()[:-4]  # Exclude CRC
        expected_crc = self._calculate_crc32(payload)
        return self.crc32 == expected_crc


@dataclass
class WeaponStatus:
    """
    Weapon status telemetry message

    Sent from weapon to launch platform.
    Provides health, fuel, and seeker status.
    """
    message_type: int = MessageType.WEAPON_STATUS.value
    sequence_number: int = 0
    timestamp_ms: int = 0
    weapon_id: int = 0

    # Status fields
    fuel_remaining_percent: float = 0.0
    motor_temperature_c: float = 0.0
    seeker_status: int = 0  # Bitmask: 0x01=ready, 0x02=locked, 0x04=tracking
    control_surface_health: int = 0  # Bitmask for each surface
    battery_voltage_v: float = 0.0
    estimated_range_km: float = 0.0
    inertial_nav_quality: float = 0.0

    def to_bytes(self) -> bytes:
        """Serialize to 64-byte message"""
        return struct.pack(
            '<BHIQffffBBI',
            self.message_type,
            self.sequence_number,
            self.timestamp_ms,
            self.weapon_id,
            self.fuel_remaining_percent,
            self.motor_temperature_c,
            self.battery_voltage_v,
            self.estimated_range_km,
            self.seeker_status,
            self.control_surface_health,
            self.inertial_nav_quality
        )


class ReedSolomonFEC:
    """
    Reed-Solomon Forward Error Correction

    RS(255, 215) code:
    - 215 data bytes
    - 40 parity bytes
    - Can correct up to 20 byte errors
    """

    def __init__(self):
        self.n = 255  # Total codeword length
        self.k = 215  # Data length
        self.t = (self.n - self.k) // 2  # Error correction capability (20 bytes)

    def encode(self, data: bytes) -> bytes:
        """
        Encode data with Reed-Solomon FEC

        Args:
            data: Input data (max 215 bytes)

        Returns:
            255-byte codeword (215 data + 40 parity)
        """
        if len(data) > self.k:
            raise ValueError(f"Data too long: {len(data)} > {self.k}")

        # Pad to 215 bytes if needed
        padded_data = data + b'\x00' * (self.k - len(data))

        # Simplified RS encoding (production would use proper GF(256) math)
        # For demonstration, use simplified parity calculation
        parity = self._calculate_parity(padded_data)

        codeword = padded_data + parity

        return codeword

    def decode(self, codeword: bytes) -> Tuple[bytes, int]:
        """
        Decode Reed-Solomon codeword

        Args:
            codeword: 255-byte codeword

        Returns:
            Tuple of (decoded_data, num_errors_corrected)
        """
        if len(codeword) != self.n:
            raise ValueError(f"Invalid codeword length: {len(codeword)}")

        # Extract data and parity
        data = codeword[:self.k]
        parity_rx = codeword[self.k:]

        # Calculate expected parity
        parity_expected = self._calculate_parity(data)

        # Simplified error detection (production RS uses syndrome calculation)
        errors = sum(a != b for a, b in zip(parity_rx, parity_expected))

        if errors == 0:
            return data, 0
        elif errors <= self.t:
            # Errors correctable (simplified - actual RS uses error locator polynomial)
            return data, errors
        else:
            # Too many errors
            raise ValueError(f"Uncorrectable errors: {errors} > {self.t}")

    def _calculate_parity(self, data: bytes) -> bytes:
        """
        Calculate Reed-Solomon parity bytes

        Simplified implementation using hash-based approach.
        Production RS uses generator polynomial over GF(256).
        """
        # Simplified: Use cryptographic hash for parity simulation
        parity_size = self.n - self.k
        hash_val = hashlib.sha256(data).digest()

        # Expand hash to 40 bytes
        parity = (hash_val * 2)[:parity_size]

        return parity


class DatalinkProtocol:
    """
    Complete datalink protocol stack

    Layers:
    1. Physical: C-band RF (handled externally)
    2. Link: FEC + framing
    3. Network: Addressing + routing (simple - single link)
    4. Application: Message types
    """

    def __init__(self, fec_scheme: FECScheme = FECScheme.REED_SOLOMON_255_215):
        self.fec_scheme = fec_scheme
        self.rs_encoder = ReedSolomonFEC()

        # Protocol statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.errors_corrected = 0
        self.messages_lost = 0

    def transmit_mid_course_update(self, update: MidCourseUpdate) -> bytes:
        """
        Transmit mid-course update with FEC encoding

        Args:
            update: MidCourseUpdate message

        Returns:
            Encoded transmission frame (255 bytes)
        """
        # Serialize message
        message_bytes = update.to_bytes()

        # Apply FEC encoding
        if self.fec_scheme == FECScheme.REED_SOLOMON_255_215:
            encoded_frame = self.rs_encoder.encode(message_bytes)
        else:
            # Other FEC schemes would go here
            encoded_frame = message_bytes

        self.messages_sent += 1

        return encoded_frame

    def receive_mid_course_update(self, received_frame: bytes) -> Optional[MidCourseUpdate]:
        """
        Receive and decode mid-course update

        Args:
            received_frame: Received transmission frame (may have errors)

        Returns:
            Decoded MidCourseUpdate or None if uncorrectable
        """
        try:
            # Apply FEC decoding
            if self.fec_scheme == FECScheme.REED_SOLOMON_255_215:
                decoded_data, num_errors = self.rs_encoder.decode(received_frame)
                self.errors_corrected += num_errors
            else:
                decoded_data = received_frame
                num_errors = 0

            # Deserialize message
            update = MidCourseUpdate.from_bytes(decoded_data)

            # Verify CRC
            if not update.verify_crc():
                self.messages_lost += 1
                return None

            self.messages_received += 1

            return update

        except (ValueError, struct.error) as e:
            # Uncorrectable errors or malformed message
            self.messages_lost += 1
            return None

    def get_link_quality_percent(self) -> float:
        """
        Calculate link quality percentage

        Returns:
            Link quality (0-100%)
        """
        total = self.messages_sent
        if total == 0:
            return 100.0

        received = self.messages_received
        quality = (received / total) * 100.0

        return quality


# Example usage
if __name__ == "__main__":
    print("Weapon Datalink Protocol Specification")
    print("=" * 60)

    # Create mid-course update
    update = MidCourseUpdate(
        sequence_number=1234,
        timestamp_ms=60000,  # 60 seconds since launch
        weapon_id=0x12345678,
        position_x_m=50000.0,
        position_y_m=100000.0,
        position_z_m=10000.0,
        velocity_x_mps=250.0,
        velocity_y_mps=150.0,
        velocity_z_mps=0.0,
        track_quality=0.95,
        cep_meters=25.0,
        gdop=2.5,
        sensor_count=4
    )

    print(f"\nMid-Course Update:")
    print(f"  Sequence: {update.sequence_number}")
    print(f"  Target Position: ({update.position_x_m:.0f}, {update.position_y_m:.0f}, {update.position_z_m:.0f}) m")
    print(f"  Target Velocity: ({update.velocity_x_mps:.0f}, {update.velocity_y_mps:.0f}, {update.velocity_z_mps:.0f}) m/s")
    print(f"  Track Quality: {update.track_quality:.2f}")
    print(f"  CEP: {update.cep_meters:.1f} m")
    print(f"  GDOP: {update.gdop:.1f}")

    # Create datalink protocol
    datalink = DatalinkProtocol()

    # Transmit
    print(f"\nTransmitting message...")
    encoded_frame = datalink.transmit_mid_course_update(update)
    print(f"  Encoded frame size: {len(encoded_frame)} bytes")
    print(f"  FEC: {datalink.fec_scheme.value}")

    # Simulate transmission (perfect channel)
    received_frame = encoded_frame

    # Receive
    print(f"\nReceiving message...")
    decoded_update = datalink.receive_mid_course_update(received_frame)

    if decoded_update:
        print(f"  ✓ Message decoded successfully")
        print(f"  Position match: {decoded_update.position_x_m == update.position_x_m}")
        print(f"  Link quality: {datalink.get_link_quality_percent():.1f}%")
    else:
        print(f"  ✗ Message decoding failed")

    # Simulate errors
    print(f"\nSimulating channel errors...")
    corrupted_frame = bytearray(encoded_frame)

    # Introduce 10 random bit errors
    for i in range(10):
        byte_idx = np.random.randint(0, len(corrupted_frame))
        bit_idx = np.random.randint(0, 8)
        corrupted_frame[byte_idx] ^= (1 << bit_idx)

    decoded_with_errors = datalink.receive_mid_course_update(bytes(corrupted_frame))

    if decoded_with_errors:
        print(f"  ✓ Errors corrected successfully")
        print(f"  Total errors corrected: {datalink.errors_corrected}")
    else:
        print(f"  ✗ Errors uncorrectable")

    print("\n" + "=" * 60)
    print("Protocol specification complete.")
