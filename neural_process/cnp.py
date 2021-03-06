import tensorflow as tf

from neural_process.module.base import Encoder, Decoder, GaussianProb

class ConditionalNP:
    """Conditional Neural Process
    Attributes:
        encoder: Encoder, context encoder
        decoder: Decoder, context decoder,
        normal_dist: GaussianProb, converter from decoded context to gaussian dist
    """
    def __init__(self, enc_output_sizes, dec_output_sizes):
        """Initializer
        Args:
            enc_output_sizes: List[int], number of hidden units for encoder
            dec_output_sizes: List[int], number of hidden units for decoder
        """
        self.encoder = Encoder(enc_output_sizes)
        self.decoder = Decoder(dec_output_sizes[:-1])
        self.normal_dist = GaussianProb(dec_output_sizes[-1], multivariate=True)

    def __call__(self, context, query):
        # context: (tf.Tensor, tf.Tensor)
        context = self.encoder(context)

        n_query = tf.shape(query)[1]
        context = tf.tile(tf.expand_dims(context, 1),
                          [1, n_query, 1])

        rep = self.decoder(context, query)
        dist, mu, sigma = self.normal_dist(rep)

        return dist, mu, sigma

    def loss(self, context, query, target):
        dist, _, _ = self(context, query)
        log_prob = dist.log_prob(target)
        # maximize log liklihood
        return -tf.reduce_mean(log_prob)
