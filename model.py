#lightning module
import pytorch_lightning as pl
import torchvision
import torch
from sklearn.metrics import precision_recall_fscore_support
from torchvision import transforms as tr

pipeline = tr.Compose(
             [tr.Grayscale(num_output_channels=3),
              tr.RandomRotation(degrees = 270),
              tr.RandomHorizontalFlip(),
              tr.RandomVerticalFlip(),
              tr.RandomPerspective(distortion_scale=0.3, p=0.5)])
pipeline2 = tr.Compose(
    [tr.Grayscale(num_output_channels=3)])


loss_func = torch.nn.BCELoss()
activation_func  = torch.nn.Sigmoid()

class InfractionDetectionModel(pl.LightningModule):
    def __init__(self, train_dataset=None, val_dataset=None, model=None, col_fn=None, learning_rate=5e-5, num_loading_cpus=2, batch_size=1):
        super().__init__() 
        self.model =  model
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.col_fn = col_fn
        self.learning_rate = learning_rate
        self.num_loading_cpus = num_loading_cpus
        self.batch_size = batch_size
    
    def forward(self,x):
        f = activation_func(self.model.forward(x))
        return f
    
    def training_step(self, batch, batch_idx):
        x = pipeline(batch['data'])
        x = batch['data']
        y = torch.unsqueeze(batch['labels'],0).float()
        y_hat = self.forward(x.float())

        print('y_hat ', y_hat, " y", y)
        loss = loss_func(y_hat,y)
        return loss
        
    def validation_step(self, batch, batch_idx):
        x = pipeline2(batch['data'])
        y = torch.unsqueeze(batch['labels'],0).float()
        with torch.no_grad():
            y_hat = self.forward(x.float())
            loss = loss_func(y_hat,y)
            y = torch.round(y).tolist()[0]
            y_hat = torch.round(y_hat).tolist()[0]
            precision, recall, fscore, support = precision_recall_fscore_support(y, y_hat, average='micro')
            self.log("val_loss", loss)
            self.log("precision", precision)
            self.log("recall", recall)
            return {"val_loss" : loss, "precision" : precision, "recall" : recall}
    
    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train_dataset,batch_size=self.batch_size,collate_fn=self.col_fn)
    
    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.val_dataset,batch_size=self.batch_size,collate_fn=self.col_fn)     
    
    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.learning_rate)