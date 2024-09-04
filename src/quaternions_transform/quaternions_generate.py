import numpy as np
from filterpy.kalman import ExtendedKalmanFilter as EKF

def quaternion_multiply(q1, q2):
    """Multiplies two quaternions."""
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2
    ])

def normalize_quaternion(q):
    return q / np.linalg.norm(q)

class IMU_EKF(EKF):
    def __init__(self, dt):
        super().__init__(dim_x=4, dim_z=6)
        self.dt = dt
        
        # Initialize quaternion state
        self.x = np.array([1, 0, 0, 0])  # Initial quaternion [q_w, q_x, q_y, q_z]
        
        # State covariance matrix
        self.P *= 0.01  # Small initial uncertainty
        
        # Process noise covariance
        self.Q = np.eye(4) * 0.01  # Adjust process noise
        
        # Measurement noise covariance
        self.R = np.eye(6) * 0.1  # Adjust measurement noise for accelerometer + magnetometer
    
    def predict(self, gyroscope_data):
        """Predict step: Use gyroscope to predict new state."""
        q = self.x
        gx, gy, gz = gyroscope_data  # Angular velocity
        
        # Compute quaternion derivative from gyroscope data
        q_dot = 0.5 * quaternion_multiply(q, [0, gx, gy, gz])
        
        # Update the quaternion state
        self.x = normalize_quaternion(self.x + q_dot * self.dt)
    
    def h(self, x):
        """Measurement function: Expected accelerometer and magnetometer readings from quaternion."""
        # Use quaternion to compute expected gravity and magnetic field directions
        gx, gy, gz = self.get_gravity_vector(x)
        mx, my, mz = self.get_magnetic_field_vector(x)
        
        # Return the concatenation of gravity and magnetic field vectors
        return np.array([gx, gy, gz, mx, my, mz])
    
    def get_gravity_vector(self, q):
        """Compute gravity vector from quaternion."""
        q_w, q_x, q_y, q_z = q
        g_x = 2 * (q_x * q_z - q_w * q_y)
        g_y = 2 * (q_w * q_x + q_y * q_z)
        g_z = q_w**2 - q_x**2 - q_y**2 + q_z**2
        return g_x, g_y, g_z
    
    def get_magnetic_field_vector(self, q):
        """Compute magnetic field vector from quaternion."""
        # This is a simplified model. You may need a more accurate model for magnetometer.
        return 1, 0, 0  # Assume some reference magnetic field in the x direction
    
    def HJacobian(self, x):
        """Jacobian of the measurement function with respect to the state (quaternion)."""
        # For simplicity, use an identity matrix as a placeholder.
        # In reality, you would compute the partial derivatives of h(x) with respect to x.
        return np.eye(6, 4)  # 6 measurements (3 from accelerometer, 3 from magnetometer), 4 states (quaternion)

    def update(self, accel_data, mag_data):
        """Measurement update step: Use accelerometer and magnetometer data to correct state."""
        z = np.hstack((accel_data, mag_data))
        super().update(z, self.HJacobian, self.h)


# Example IMU data (gyroscope, accelerometer, magnetometer)
gyro_data = np.array([0.01, 0.02, 0.03])  # Angular velocity (rad/s)
accel_data = np.array([0.0, 0.0, 9.81])   # Accelerometer (gravity vector)
mag_data = np.array([0.3, 0.1, 0.2])      # Magnetometer (magnetic field vector)

# Create the EKF instance
dt = 1/52  # Sample rate
ekf = IMU_EKF(dt)

# Predict step: Use gyroscope to predict the quaternion
ekf.predict(gyro_data)

# Update step: Use accelerometer and magnetometer to correct the quaternion
ekf.update(accel_data, mag_data)

# Get the estimated quaternion
q = ekf.x
print("Estimated Quaternion:", q)

