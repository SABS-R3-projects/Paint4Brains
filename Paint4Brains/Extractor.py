import tensorflow as tf
import numpy as np
from skimage.transform import resize
import os

PB_FILE = os.path.join(os.path.dirname(__file__), "saved_models", "deepbrain_extractor.pb")
CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "models")


class Extractor:
    """Extractor class for Paint4Brains.

    This class contains the main extraction functions required.

    Returns:
        prob (np.array): Probability of each voxel being brain tissue or not.

    """
    def __init__(self):
        self.SIZE = 128
        self.load_pb()

    def load_pb(self):
        """ Load the neural network with the appropriate weights into the Extractor class.

        This function is run when the class is initialized
        """
        graph = tf.compat.v1.Graph()
        self.sess = tf.compat.v1.Session(graph=graph)
        with tf.compat.v1.gfile.FastGFile(PB_FILE, 'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
            with self.sess.graph.as_default():
                tf.import_graph_def(graph_def)

        self.img = graph.get_tensor_by_name("import/img:0")
        self.training = graph.get_tensor_by_name("import/training:0")
        self.dim = graph.get_tensor_by_name("import/dim:0")
        self.prob = graph.get_tensor_by_name("import/prob:0")
        self.pred = graph.get_tensor_by_name("import/pred:0")

    def run(self, image):
        """ Performs extraction on the given image

        Runs the given image through the deepbrain network and returns a probability mask.
        :param image:

        Args:
            image (np.array): Original 3D brain mri volume

        Returns:
            prob (np.array): Probability of each voxel being brain tissue or not.
        """
        shape = image.shape
        img = resize(image, (self.SIZE, self.SIZE, self.SIZE), mode='constant', anti_aliasing=True)
        img = (img / np.max(img))
        img = np.reshape(img, [1, self.SIZE, self.SIZE, self.SIZE, 1])

        prob = self.sess.run(self.prob, feed_dict={self.training: False, self.img: img}).squeeze()
        prob = resize(prob, (shape), mode='constant', anti_aliasing=True)
        return prob
