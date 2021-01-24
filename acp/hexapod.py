import math

def sq(x: float) -> float:
    return x*x

class hexapod:

    def __init__(self):

        self.legs = [
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0],
            [0,0,0]   
        ]
        self.COXA_LENGTH = 51           #leg part lengths
        self.FEMUR_LENGTH = 65
        self.TIBIA_LENGTH = 121



    def set_joint(self, leg_id: int, joint_id: int, value: int):
        self.legs[leg_id, joint_id] = value

    def set_leg(self, leg_id: int, coxa: int, femur: int, tibia: int):
        self.set_joint(leg_id, 0, coxa)
        self.set_joint(leg_id, 1, femur)
        self.set_joint(leg_id, 2, tibia)



    def leg_ik(int leg_number, X: float, Y: float, Z: float):
        #compute target femur-to-toe (L3) length
        L0 = sqrt(sq(X) + sq(Y)) - self.COXA_LENGTH
        L3 = sqrt(sq(L0) + sq(Z))

        #process only if reach is within possible range (not too long or too short!)
        if(L3 < (self.TIBIA_LENGTH+self.FEMUR_LENGTH)) and (L3 > (self.TIBIA_LENGTH-self.FEMUR_LENGTH)):
            #compute tibia angle
            phi_tibia = math.acos((sq(self.FEMUR_LENGTH) + sq(self.TIBIA_LENGTH) - sq(L3))/(2*self.FEMUR_LENGTH*self.TIBIA_LENGTH))
            theta_tibia = phi_tibia*RAD_TO_DEG - 23.0 + TIBIA_CAL[leg_number]
            theta_tibia = constrain(theta_tibia, 0.0, 180.0)
        
            #compute femur angle
            gamma_femur = math.atan2(Z,L0)
            phi_femur = math.acos((sq(self.FEMUR_LENGTH) + sq(L3) - sq(self.TIBIA_LENGTH))/(2*self.FEMUR_LENGTH*L3))
            theta_femur = (phi_femur + gamma_femur)*RAD_TO_DEG + 14.0 + 90.0 + FEMUR_CAL[leg_number]
            theta_femur = constrain(theta_femur,0.0,180.0)  

            #compute coxa angle
            theta_coxa = math.atan2(X,Y)*RAD_TO_DEG + COXA_CAL[leg_number]

            #output to the appropriate leg
            theta_coxa_corraction = (leg_number+1)*45
            if leg_number > 2 and theta_coxa < 0:
                theta_coxa_corraction = - 1 * (6 - leg_number) * 45
            self.set_leg(leg_number, theta_coxa+theta_coxa_corraction, theta_femur, theta_tibia)
            
