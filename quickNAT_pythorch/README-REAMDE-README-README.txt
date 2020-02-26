Notes for working with QuickNAT
=================================

Note: this is for starting with a clean QuickNAT install! 
-----------------------------------------------------------

-- To clone QuickNAT, use this command: 

git clone https://github.com/ai-med/quickNAT_pytorch.git

-- This will take QuickNAT into the home directory
-- I like working into a virtual environment, which is why I create one and then open it using the following in the QuickNAT folder

python3 -m venv env
source env/bin/activate

-- The next step is installing QuickNAT. I use the github command from the original repo:

pip install -r requirements.txt

-- Although when we first did it a month ago, we got a few errors, the author has not updated requirements.txt and the process ran smooth. To check that everything is installed and working, run the following command again. It should say that everything is installed and good.

pip install -r requirements.txt

--Okay. Now everything should be a clean install. Now let's move to running it!



Running the Model
-----------------------------------------------

-- For this clean install, I'm going to start by trying to run a freesurfer file (hope this works!)
-- To run stuff, we will keep to the info in the github repo on running in the bulk eval mode. We don't care about training the model as we are using the weights provided by the author.
-- Before running the model, we need to adjust the settings. We might also need to adjust some of the model paramters, in the code, as we are running this on a CPU. Pythorch is weird, in the sence that if you train your model on a GPU, it will set the default operation mode for the trained model to GPUs. However, our computers don't have GPUs, so we need to run it on CPUs. As I test this today (Thu, 12/12) I will add info to this document if this is the case.
-- Before running anything, we need to modify the settings. These are in 'settings_eval.ini'.

-------- NOTE FOR FUTURE USE: HAVE THESE DONE AS USER INPUTS, OR VIA A GUY, RATHER THAN MANUAL SETTINGS

-- These are the settings that I am changing in 'settings_eval.ini', using VSCode. I am stating only the lines I am changing or that I would change, based on the inputs. Leave everything else as it is for now!

->(line2)-> device = 0 (original device is set to 1. This means it will ask QuickNAT to run on a GPU. Setting to 0 tells it to use a CPU)
->(line5)-> data_dir = "../quickNAT_pytorch/data_input" (this needs to be changed, as the directory indicated does not exist). Thus, I created a new directory named 'data_input' where to put the input files)
->(line7)-> directory_struct = "FS" (Valid options are "FS" or "Linear". If you input data directory is similar to FreeSurfer, i.e. data_dir/<Data_id>/mri/orig.mgz then use "FS". If the entries are data_dir/<Data_id> use "Linear".)
->(line9)-> volumes_txt_files = "test_list.txt" (Path to the '.txt' file where the data_ID names are stored. If directory_struct is "FS" the entries should be only the folder names, whereas if it is "Linear" the entry name should be the file names with the file extensions)
->(line11)-> save_predictions_dir = "output_file" (I created a new output file in which to output my predictions)
->(line13)-> view_agg = "True" (We want it to use both networks, not only the coronal one).

-- More info on how the setting file works can be found here: https://github.com/ai-med/quickNAT_pytorch
-- When tryint to run the code, I realize that I am getting this error: RuntimeError: Attempting to deserialize object on a CUDA device but torch.cuda.is_available() is False. If you are running on a CPU-only machine, please use torch.load with map_location=torch.device('cpu') to map your storages to the CPU.
-- This is because of the previous thing I mentioned, with running the network on a CPU rather than a GPU
-- To solve this, go to the following file: >..>utils>evaluator.py
-- Go to the line 311 and 313, and replace the codes there with the following:

    model1 = torch.load(coronal_model_path, map_location=torch.device('cpu'))

    model2 = torch.load(axial_model_path, map_location=torch.device('cpu'))

-- Hopefully this has taken care of all stuff, and killed all the bugs. Now I will try to make this work!

        .--.       .--.
    _  `    \     /    `  _
     `\.===. \.^./ .===./`
            \/`"`\/
         ,  | y2k |  ,
        / `\|;-.-'|/` \
       /    |::\  |    \
    .-' ,-'`|:::; |`'-, '-.
        |   |::::\|   | 
        |   |::::;|   |
        |   \:::://   |
        |    `.://'   |
       .'             `.
    _,'                 `,_


-- Going into the data_input folder, I paste there 80yearold.nii in there. I also add this "80yearold.nii" text to the test_list.txt file.

-- So, to run the model, type in this command:

python run.py --mode=eval_bulk

-- WARNING: IF RAN ON A DTC LAPTOP, YOU ARE RUNNING A GPU-BASED CODE ON A CPU! A GPU IS ABOUT 200X FASTER THAN A CPU FOR THIS, SO YOU WILL OVERWORK YOUR CPU. THIS MEANS YOUR LAPTOP WILL MAKE A LOT OF NOISE AND WILL HEAT UP (and hopefully not die in the process). THIW WILL LAST FOR ABOUT 1 HOUR PER RUN!
-- I RECOMMEND YOU RUN THIS ON ONE OF THE DESKTOP MACHINES!!!





-- The author recommends that before deploying the model we need to standardize the MRI scans. Use the following command from FreeSurfer. For the first runs I will try to get it to work with our existing files. 

mri_convert --conform <input_volume.nii> <out_volume.nii>


-- This saves the segmentation files at nifti files in the destination folder. Also in the folder, a '.csv' file is generated which provides the volume estimates of the brain structures with subject ids for all the processed volumes.
-- Also uncertainty flag is set, another two '.csv' files are created with structure-wise uncertainty (CVs and IoU) for quality control of the segmentations.
