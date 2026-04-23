pragma circom 2.0.0;

template HashCheck() {
    signal input data;
    signal input hash;
    signal output valid;

    // 简化验证（先做 demo）
    valid <== data * data - hash;
}

component main = HashCheck();