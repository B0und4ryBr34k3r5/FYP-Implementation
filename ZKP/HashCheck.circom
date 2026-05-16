pragma circom 2.0.0;

template HashCheck() {
    signal input data;
    signal input hash;
    signal output valid;

    // Using simple function for demo
    valid <== data * data - hash;
}

component main = HashCheck();