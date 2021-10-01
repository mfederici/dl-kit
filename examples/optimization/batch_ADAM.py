from pytorch_lightning.utilities.types import STEP_OUTPUT
from torch.utils.data import DataLoader
from torch.optim import Adam

from framework.optimization.base import Optimization
from examples.models.types import Model


class AdamBatchOptimization(Optimization):
    def __init__(self,
                 model: Model,              # The model to optimize
                 data: dict,                # The dictionary of Datasets defined in the previous 'Data' section
                 num_workers: int,          # Number of workers for the data_loader
                 batch_size: int,           # Batch size
                 lr: float,                 # Learning rate
                 pin_memory: bool = True    # Flag to enable memory pinning
                 ):
        super(AdamBatchOptimization, self).__init__()

        self.model = model
        self.data = data

        self.batch_size = batch_size
        self.num_workers = num_workers
        self.lr = lr
        self.pin_memory = pin_memory

    def log_counters(self) -> None:
        for counter, value in self.counters.items():
            self.log(counter, value)

    # this overrides the pl.LightningModule train_dataloader which is used by the Trainer
    def train_dataloader(self):
        return DataLoader(self.data['train'],
                          batch_size=self.batch_size,
                          num_workers=self.num_workers,
                          shuffle=True,
                          pin_memory=self.pin_memory)

    def training_step(self, data, data_idx) -> STEP_OUTPUT:
        loss_items = self.model.compute_loss(data, data_idx)
        for name, value in loss_items.items():
            self.log('Train/%s' % name, value)
        self.counters['iteration'] += 1

        self.log_counters()

        return loss_items

    def configure_optimizers(self):
        return Adam(self.model.parameters(), lr=self.lr)
