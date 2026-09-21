import torch
import torch.nn as nn
import torchvision.models as models

class DeepfakeVideoModel(nn.Module):
    def __init__(self, config_path: str = "config.yaml"):
        super(DeepfakeVideoModel, self).__init__()
        
        # Load config or use defaults
        import yaml
        import os
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f).get("model", {})
        except Exception:
            config = {}
            
        backbone_name = config.get("backbone_name", "resnet18")
        hidden_size = config.get("hidden_size", 256)
        num_layers = config.get("num_layers", 2)
        dropout_rate = config.get("dropout", 0.5)
        
        # 1. Visual Backbone
        if backbone_name == "resnet18":
            # Load pretrained ResNet18
            resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            # Remove the final classification layer (fc) to just get feature maps
            self.feature_dim = resnet.fc.in_features
            self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        else:
            raise ValueError(f"Unsupported backbone: {backbone_name}")
            
        # 2. Temporal Sequence Model (LSTM)
        self.lstm = nn.LSTM(
            input_size=self.feature_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_rate if num_layers > 1 else 0
        )
        
        # 3. Final Classifiers
        # Frame-level classifier (for suspicious frame evidence)
        self.frame_classifier = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Video-level classifier
        self.video_classifier = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, 1),
            nn.Sigmoid()  # Outputs probability of FAKE
        )

    def forward(self, x):
        """
        x shape: (batch_size, seq_len, C, H, W)
        Returns:
            video_prob: probability of video being fake (batch_size, 1)
            frame_probs: probability of each frame being fake (batch_size, seq_len, 1)
        """
        batch_size, seq_len, c, h, w = x.size()
        
        # Reshape to (batch_size * seq_len, C, H, W) to process all frames through CNN
        x = x.view(batch_size * seq_len, c, h, w)
        
        # Extract features using backbone
        features = self.backbone(x) # (batch_size * seq_len, feature_dim, 1, 1)
        features = features.view(batch_size, seq_len, self.feature_dim)
        
        # Pass through temporal model
        lstm_out, (h_n, c_n) = self.lstm(features) # lstm_out: (batch_size, seq_len, hidden_size)
        
        # Frame-level predictions
        frame_probs = self.frame_classifier(lstm_out) # (batch_size, seq_len, 1)
        
        # Video-level prediction using the last hidden state of the LSTM
        # h_n shape: (num_layers, batch_size, hidden_size) -> take the last layer
        last_hidden = h_n[-1, :, :] # (batch_size, hidden_size)
        video_prob = self.video_classifier(last_hidden) # (batch_size, 1)
        
        return video_prob, frame_probs

if __name__ == "__main__":
    model = DeepfakeVideoModel()
    print("Model architecture loaded successfully.")
    print(model)
