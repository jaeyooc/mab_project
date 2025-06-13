# linucb_arm.py
from __future__ import annotations
import numpy as np

class LinUCBDisjointArm:
    def __init__(self, arm_index, dim, alpha): 
        self.arm_index = arm_index
        self.alpha = alpha

        # A : (dxd) matrix = D_a.T * D_a + I_d
        # the inverse of A is used in ridge regression
        self.A = np.eye(dim)  # A_a <- I_d initialize

        # b: (d x 1) corresponding response vector
        # equals to D_a.T * c_a in ridge regression formula
        self.b = np.zeros((dim,1)) # initialize b_a <- 0_dx1
    
    def ucb(self, x:np.ndarray) -> float:
        # reshape covariates input into (dx1) shape vector
        x = x.reshape(-1,1)

        # find A inverse for ridge regression
        A_inv = np.linalg.inv(self.A)

        #perform ridge regression to obtain estimate of covariate c
        # theta is (dx1) dimension vector
        theta = A_inv @ self.b

        #find ucb based on p formulation (mean + std_dev)
        # p is (1x1) dimension vector
        mean = float(theta.T @ x)
        std = self.alpha * np.sqrt(float(x.T @ A_inv @ x))
        p = mean + std

        return p

    def update(self, reward:float, x: np.ndarray) -> None:
        """
        update: A_a <- A_a + x @ x.T
        b_a <- b_a + rx
        """
        # reshape covariates input into (d x 1) shape vector
        x = x.reshape(-1,1)

        # update A which is (dxd) matrix
        self.A += x @ x.T   

        # update b which is (dx1) vec
        # reward is scalar
        self.b += reward * x
    
