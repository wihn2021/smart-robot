import os
FlowerClasses = ['bailianhua',
 'chuju',
 'hehua',
 'juhua',
 'lamei',
 'lanhua',
 'meiguihua',
 'shuixianhua',
 'taohua',
 'yinghua',
 'yuanweihua',
 'zijinghua']

for i, c in enumerate(FlowerClasses):
    ClassDir = f"../bot4/data/train/{c}"
    print(ClassDir)
    for root, dirs, files in os.walk(ClassDir):
        print(root)
        for file in files[:-1]:
            print(f"add {ClassDir}/{file} to train")

