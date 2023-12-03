import numpy as np

def load_tag_pos():
    """
    Returns:
    tuple: A tuple containing the expanded tag positions, centers, and screens.
        - tag_poses (list): List of expanded tag positions.
        - centers (list): List of center positions.
        - screens (list): List of screen positions.
    """
    def expand(LL):
        LL = np.append(LL, 0)
        a = np.array([
            [0, 0,0], [5, 0,0], [5, 5,0], [0, 5,0]
        ])
        return a + LL

    def expand_2(MM):
        z_tag = np.array([39.8])
        NN = np.append(MM, z_tag)
        return NN
    
    def expand_4(n, op):
        if op == '+x':
            a = np.array([
            [0,0,0],[5,0,0],[5,0,-5],[0,0,-5]
            ])
        if op == '-x':
            a = np.array([
            [0,0,0],[-5,0,0],[-5,0,-5],[0,0,-5]
            ])
        if op == '+y':
            a = np.array([
            [0,0,0],[0,5,0],[0,5,-5],[0,0,-5]
            ])
        if op == '-y':
            a = np.array([
            [0,0,0],[0,-5,0],[0,-5,-5],[0,0,-5]
            ])
        return a + n
    
    def expand_5(n, op):
        if op == "+x":
            a = np.array([
                [-14.6, 0, -4.5], [-8.6, 0, -4.5], [-8.6, 0, -14.8], [-14.6, 0, -14.8]
            ])
        if op == "-x":
            a = np.array([
                [14.6, 0, -4.5], [8.6, 0, -4.5], [8.6, 0, -14.8], [14.6, 0, -14.8]
            ])
        if op == "+y":
            a = np.array([
                [0 ,-14.6, -4.5], [0, -8.6, -4.5], [0, -8.6, -14.8], [0, -14.6, -14.8]
            ])
        if op == "-y":
            a = np.array([
                [0 ,14.6, -4.5], [0, 8.6, -4.5], [0, 8.6, -14.8], [0, 14.6, -14.8]
            ])
        return a+n
    
    tag_poses = [None] * 66
    centers = []
    screens = [None] * 37
    tag_poses[37] = expand([166, 287])
    tag_poses[38] = expand([231.3, 287.5])
    tag_poses[39] = expand([9.5, 250])
    tag_poses[40] = expand([48.7, 266])
    tag_poses[41] = expand([279.5, 255])
    tag_poses[42] = expand([278, 182])
    tag_poses[43] = expand([271.5, 36])
    tag_poses[44] = expand([263, 108])
    tag_poses[45] = expand([225, 126])
    tag_poses[46] = expand([226.1, 62])
    tag_poses[47] = expand([114.2, 60])
    tag_poses[48] = expand([65.5, 23])
    tag_poses[49] = expand([22.5, 24.5])
    tag_poses[50] = expand([80, 95])
    tag_poses[51] = expand([12.4, 142])
    tag_poses[52] = expand([12.5, 187])
    tag_poses[53] = expand([126, 237])
    tag_poses[54] = expand([143, 141])
    tag_poses[55] = expand([80.5, 148])
    tag_poses[56] = expand([164, 54.4])
    tag_poses[57] = expand([239, 213.5])
    tag_poses[58] = expand([205, 241])
    tag_poses[59] = expand([199.5, 141.5])
    tag_poses[60] = expand([78.5, 236.5])
    tag_poses[61] = expand([122, 156.5])

    ## 11/11 11:33 修改，下面不能改！
    tag_poses[1] = expand_2([196, 10])
    tag_poses[4] = expand_2([216, 5])
    tag_poses[3] = expand_2([221, 25])
    tag_poses[2] = expand_2([201, 30])
    
    tag_poses[7] = expand_2([116.5, 11.5])
    tag_poses[6] = expand_2([136.5, 6.5])
    tag_poses[5] = expand_2([141.5, 26.5])
    tag_poses[8] = expand_2([121.5, 31.5])

    tag_poses[10] = expand_2([14.5, 59.5])
    tag_poses[9] = expand_2([34.5, 54.5])
    tag_poses[12] = expand_2([39.5, 74.5])
    tag_poses[11] = expand_2([19.5, 79.5])

    tag_poses[13] = expand_2([69.5, 186])
    tag_poses[14] = expand_2([89.5, 181])
    tag_poses[16] = expand_2([94.5, 201])
    tag_poses[15] = expand_2([74.5, 206])

    tag_poses[19] = expand_2([92, 268])
    tag_poses[18] = expand_2([112, 263])
    tag_poses[17] = expand_2([117, 283])
    tag_poses[20] = expand_2([97, 288])

    tag_poses[21] = expand_2([154.5, 189])
    tag_poses[22] = expand_2([174.5, 184])
    tag_poses[23] = expand_2([179.5, 204])
    tag_poses[24] = expand_2([159.5, 209])

    tag_poses[26] = expand_2([235., 251.5])
    tag_poses[28] = expand_2([255., 246.5])
    tag_poses[27] = expand_2([260., 266.5])
    tag_poses[25] = expand_2([240., 271.5])

    tag_poses[29] = expand_2([235.5, 150.8])
    tag_poses[32] = expand_2([255.5, 145.8])
    tag_poses[31] = expand_2([260.5, 165.8])
    tag_poses[30] = expand_2([240.5, 170.8])

    tag_poses[35] = expand_2([158, 90])
    tag_poses[36] = expand_2([178, 85])
    tag_poses[33] = expand_2([183, 105])
    tag_poses[34] = expand_2([163, 110])

    tag_ori = [None] * 66
    for i in range(9):
        l = []
        for j in range(1,5):
            l.append(tag_poses[i*4+j])
        center = np.mean(l, axis=0)
        for index, p in enumerate(l):
            if p[0] > center[0]:
                if p[1] > center[1]:
                    t = expand_4(p, '+y')
                    t2 = expand_5(p, '+y')
                    t3 = 0
                else:
                    t = expand_4(p, '+x')
                    t2 = expand_5(p, '+x')
                    t3 = 90
            else:
                if p[1] > center[1]:
                    t = expand_4(p, '-x')
                    t2 = expand_5(p, '-x')
                    t3 = 90
                else:
                    t = expand_4(p, '-y')
                    t2 = expand_5(p, '-y')
                    t3 = 0
            tag_poses[i*4+index+1] = t
            screens[i*4+index+1] = t2
            tag_ori[i*4+index+1] = t3
        centers.append(center)

    return tag_poses, centers, screens , tag_ori