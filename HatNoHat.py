#lightning module
import pytorch_lightning as pl
import torchvision
import torch

F = torch.nn.BCEWithLogitsLoss()
M = torch.nn.Sigmoid()

class HatNoHat(pl.LightningModule):
    def __init__(self, train_dataset, val_dataset, model, col_fn, learning_rate=5e-5, num_loading_cpus=1, batch_size=1):
        super().__init__() 
        self.model =  model
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.col_fn = col_fn
        self.learning_rate = learning_rate
        self.num_loading_cpus = num_loading_cpus
        self.batch_size = batch_size
    
    def forward(self,x):
        f = self.model.forward(x)
        return f
    
    def training_step(self, batch, batch_idx):
        x = batch['data']
        #print('x ', x)
        y = torch.unsqueeze(batch['labels'],0).float()
        #print('y ', y)
        y_hat = self.forward(x.float())
        print('y_hat ', y_hat)
        output = F(y_hat,y)
        #print('loss ', output)
        return output
        
    def validation_step(self, batch, batch_idx):
        x = batch['data']
        #print('x ', x)
        y = torch.unsqueeze(batch['labels'],0).float()
        #print('y ', y)
        y_hat = self.forward(x.float())
        #print('y_hat ', y_hat)
        output = F(y_hat,y)
        #print('loss ', loss)
        return output
    
    def train_dataloader(self):
        return torch.utils.data.DataLoader(self.train_dataset,batch_size=self.batch_size,collate_fn=self.col_fn)
    
    def val_dataloader(self):
        return torch.utils.data.DataLoader(self.val_dataset,batch_size=self.batch_size,collate_fn=self.col_fn)     
    
    def configure_optimizers(self):
        return torch.optim.AdamW(self.parameters(), lr=self.learning_rate)