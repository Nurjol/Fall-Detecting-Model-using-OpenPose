# Fall detection using tf-pose-estimation

'Openpose', human pose estimation algorithm, have been implemented using Tensorflow. It also provides several variants that have some changes to the network structure for **real-time processing on the CPU or low-power embedded devices.**

Although, the FPS real-time depends on your processor and GPU. You can always consider changing configuration options through tensorflow commands.


Original Repo(Caffe) : https://github.com/CMU-Perceptual-Computing-Lab/openpose

## Fall Detection 
  3 step check process
  First step: Head position
  
     We compare the head position to head position of the previous frame: 
  
  ![image](https://user-images.githubusercontent.com/65017142/223717726-f332de36-cd7e-4da5-a338-32f05af8b7d9.png)
  
  Second step: Bounding box H/W ratio
      As we know if Bounding Box H/W ratio is bigger than 1 it means person is in standing position. 
       So if it is smaller than 1, we change the state as fallen and go to next step 
       
       Bounding box example: 
       
       Standing:
       
       ![image](https://user-images.githubusercontent.com/65017142/223718644-e626f472-13c8-4b67-9e06-0bda9621bdb0.png)

       Fallen:
       
       ![image](https://user-images.githubusercontent.com/65017142/223718700-74efca1c-737b-445a-b59c-9045c7499b0f.png)
  Third step: Check after
      We check if the fallen person gets up in next 15 frames. If not we make assumption that person has fallen. 
      
      Fallen person example:
      
      ![image](https://user-images.githubusercontent.com/65017142/223719150-c713d275-bdcb-4fb4-a339-fc8323bf22c1.png)

      Person get up example:
      
      ![image](https://user-images.githubusercontent.com/65017142/223719222-5ffbab38-35d1-441b-9aeb-e8d1a23447ce.png)

  
## Install

### Dependencies

You need dependencies below.

- python3
- tensorflow 1.4.1+
- opencv3, protobuf, python3-tk
- slidingwindow
  - https://github.com/adamrehn/slidingwindow
  - I copied from the above git repo to modify few things.
- swig

### Install

Clone the repo and install 3rd-party libraries. Unzip all zip files to the same folder without changing the name.

```bash
$ git clone https://www.github.com/ildoonet/tf-pose-estimation
$ cd tf-pose-estimation
$ pip3 install -r requirements.txt
```

## Swig

After unzipping Swig Folder swigwin-4.0.0, you need to go to start, type edit, select edit the system environment variables,
select environment variables option in 'Advanced' tab, double click on 'Path' in the user variables for <username> section.
Now, click 'New' and add the path of the swigwin-4.0.0 directory, including swigwin-4.0.0
  
Alternatively, you can also download latest swig folder according to your needs from swig website. 

Build c++ library for post processing. See : https://github.com/ildoonet/tf-pose-estimation/tree/master/tf_pose/pafprocess
```
$ cd tf_pose/pafprocess
$ swig -python -c++ pafprocess.i && python3 setup.py build_ext --inplace
```

### Package Install

Alternatively, you can install this repo as a shared package using pip.

```bash
$ git clone https://www.github.com/ildoonet/tf-pose-estimation
$ cd tf-openpose
$ python setup.py install  # Or, `pip install -e .`
```

## Models & Performances

See [experiments.md](./etc/experiments.md)

### Download Tensorflow Graph File(pb file)

Before running demo, you should download graph files. You can deploy this graph on your mobile or other platforms.

- cmu (trained in 656x368)
- mobilenet_thin (trained in 432x368)
- mobilenet_v2_large (trained in 432x368)
- mobilenet_v2_small (trained in 432x368)

CMU's model graphs are too large for git, so I uploaded them on an external cloud. You should download them if you want to use cmu's original model. Download scripts are provided in the model folder.

```
$ cd models/graph/cmu
$ bash download.sh
```

## Demo

### Test Inference

You can test the inference feature with a single image.

```
$ python run.py --model=mobilenet_thin --resize=432x368 --image=./images/p1.jpg
```

The image flag MUST be relative to the src folder with no "~", i.e:
```
--image ../../Desktop
```

Then you will see the screen as below with pafmap, heatmap, result and etc.

![inferent_result](./etcs/inference_result2.png)

### Realtime Webcam

```
$ python Fall_Detection.py --model=mobilenet_thin --resize=432x368 --video=0
```

Then you will see the realtime webcam screen with estimated poses as below. This [Realtime Result](./etcs/openpose_macbook13_mobilenet2.gif) was recored on macbook pro 13" with 3.1Ghz Dual-Core CPU.

## Python Usage

This pose estimator provides simple python classes that you can use in your applications.

See [run.py](run.py) or [Fall_Detection.py](Fall_Detection.py) as references.

```python
e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))
humans = e.inference(image)
image = TfPoseEstimator.draw_humans(image, humans, imgcopy=False)
```

If you installed it as a package,

```python
import tf_pose
coco_style = tf_pose.infer(image_path)
```

## Fall Detection

It takes the difference of position markings of head and legs to determine a Fall.

It indicates a fall by displaying text on the screen. Although, a classifier can be trained if we have enough data along with accuarte prediction.

This can be done by running it on a small video with fall occurences. Then manually check the falls and making a list manually.
Now we have the train data, we can test it on the entire video or live webcam and save it in the classifier.


## ROS Support

See : [etcs/ros.md](./etcs/ros.md)

## Training

See : [etcs/training.md](./etcs/training.md)

## References

See : [etcs/reference.md](./etcs/reference.md)
