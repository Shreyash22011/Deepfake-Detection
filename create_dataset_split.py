import os
import shutil
import random

DATASET_DIR = r"C:\DFD_Dataset"

REAL_SRC = os.path.join(DATASET_DIR, "real")
FAKE_SRC = os.path.join(DATASET_DIR, "fake")

random.seed(42)

# Split ratios
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Create folders
for split in ["train", "val", "test"]:
    for label in ["real", "fake"]:
        os.makedirs(
            os.path.join(DATASET_DIR, split, label),
            exist_ok=True
        )

def split_files(files):
    random.shuffle(files)

    total = len(files)

    train_end = int(total * TRAIN_RATIO)
    val_end = train_end + int(total * VAL_RATIO)

    train = files[:train_end]
    val = files[train_end:val_end]
    test = files[val_end:]

    return train, val, test


def copy_files(files, source_dir, destination_dir):
    for filename in files:
        source = os.path.join(source_dir, filename)
        destination = os.path.join(destination_dir, filename)

        if not os.path.exists(destination):
            shutil.copy2(source, destination)


# Get videos
real_files = [
    f for f in os.listdir(REAL_SRC)
    if f.lower().endswith(".mp4")
]

fake_files = [
    f for f in os.listdir(FAKE_SRC)
    if f.lower().endswith(".mp4")
]

print("Original dataset:")
print(f"Real: {len(real_files)}")
print(f"Fake: {len(fake_files)}")

# Split
real_train, real_val, real_test = split_files(real_files)
fake_train, fake_val, fake_test = split_files(fake_files)

# Copy real
copy_files(
    real_train,
    REAL_SRC,
    os.path.join(DATASET_DIR, "train", "real")
)

copy_files(
    real_val,
    REAL_SRC,
    os.path.join(DATASET_DIR, "val", "real")
)

copy_files(
    real_test,
    REAL_SRC,
    os.path.join(DATASET_DIR, "test", "real")
)

# Copy fake
copy_files(
    fake_train,
    FAKE_SRC,
    os.path.join(DATASET_DIR, "train", "fake")
)

copy_files(
    fake_val,
    FAKE_SRC,
    os.path.join(DATASET_DIR, "val", "fake")
)

copy_files(
    fake_test,
    FAKE_SRC,
    os.path.join(DATASET_DIR, "test", "fake")
)

print("\nSplit complete!")
print("\nREAL:")
print(f"Train: {len(real_train)}")
print(f"Val:   {len(real_val)}")
print(f"Test:  {len(real_test)}")

print("\nFAKE:")
print(f"Train: {len(fake_train)}")
print(f"Val:   {len(fake_val)}")
print(f"Test:  {len(fake_test)}")