from needle.search import Search
from needle.viewer import RichDevice, Viewer


_EXAMPLE = {
    "dataset": {
        "path": "/drive/dataset",
        "metadata": "/drive/metadata.json",
        "stats": ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    },
    "split": "/drive/split.json",
    "training": {
        "model": {
            "backbone": "resnet18",
            "head": {
                "n_classes": 10
            },
            "aux": None
        },
        "data_loader": {
            "batch_size": 128,
            "num_workers": 8,
        }
    },
    "evaluation": {
        "data_loader": {
            "batch_size": 256,
            "num_workers": 8
        }
    },
    "test": {
        "dataset": "/data/test",
        "enabled": True,
    }
}


def main():
    Viewer(Search(_EXAMPLE), RichDevice()).interactive()


if __name__ == '__main__':
    main()
