import mxnet as mx
import proposal
import proposal_target
from rcnn.config import config


def get_vgg_conv3_3(data):
    """
    shared convolutional layers
    :param data: Symbol
    :return: Symbol
    """
    # group 1
    conv1_1 = mx.symbol.Convolution(
        data=data, kernel=(3, 3), pad=(1, 1), num_filter=64, workspace=2048, name="conv1_1")
    relu1_1 = mx.symbol.Activation(data=conv1_1, act_type="relu", name="relu1_1")
    conv1_2 = mx.symbol.Convolution(
        data=relu1_1, kernel=(3, 3), pad=(1, 1), num_filter=64, workspace=2048, name="conv1_2")
    relu1_2 = mx.symbol.Activation(data=conv1_2, act_type="relu", name="relu1_2")
    pool1 = mx.symbol.Pooling(
        data=relu1_2, pool_type="max", kernel=(2, 2), stride=(2, 2), name="pool1")
    # group 2
    conv2_1 = mx.symbol.Convolution(
        data=pool1, kernel=(3, 3), pad=(1, 1), num_filter=128, workspace=2048, name="conv2_1")
    relu2_1 = mx.symbol.Activation(data=conv2_1, act_type="relu", name="relu2_1")
    conv2_2 = mx.symbol.Convolution(
        data=relu2_1, kernel=(3, 3), pad=(1, 1), num_filter=128, workspace=2048, name="conv2_2")
    relu2_2 = mx.symbol.Activation(data=conv2_2, act_type="relu", name="relu2_2")
    pool2 = mx.symbol.Pooling(
        data=relu2_2, pool_type="max", kernel=(2, 2), stride=(2, 2), name="pool2")
    # group 3
    conv3_1 = mx.symbol.Convolution(
        data=pool2, kernel=(3, 3), pad=(1, 1), num_filter=256, workspace=2048, name="conv3_1")
    relu3_1 = mx.symbol.Activation(data=conv3_1, act_type="relu", name="relu3_1")
    conv3_2 = mx.symbol.Convolution(
        data=relu3_1, kernel=(3, 3), pad=(1, 1), num_filter=256, workspace=2048, name="conv3_2")
    relu3_2 = mx.symbol.Activation(data=conv3_2, act_type="relu", name="relu3_2")
    conv3_3 = mx.symbol.Convolution(
        data=relu3_2, kernel=(3, 3), pad=(1, 1), num_filter=256, workspace=2048, name="conv3_3")
    relu3_3 = mx.symbol.Activation(data=conv3_3, act_type="relu", name="relu3_3")
    return relu3_3
def get_vgg_conv4_3(data):
    pool3 = mx.symbol.Pooling(
        data=data, pool_type="max", kernel=(2, 2), stride=(2, 2), name="pool3")
    # group 4
    conv4_1 = mx.symbol.Convolution(
        data=pool3, kernel=(3, 3), pad=(1, 1), num_filter=512, workspace=2048, name="conv4_1")
    relu4_1 = mx.symbol.Activation(data=conv4_1, act_type="relu", name="relu4_1")
    conv4_2 = mx.symbol.Convolution(
        data=relu4_1, kernel=(3, 3), pad=(1, 1), num_filter=512, workspace=2048, name="conv4_2")
    relu4_2 = mx.symbol.Activation(data=conv4_2, act_type="relu", name="relu4_2")
    conv4_3 = mx.symbol.Convolution(
        data=relu4_2, kernel=(3, 3), pad=(1, 1), num_filter=512, workspace=2048, name="conv4_3")
    relu4_3 = mx.symbol.Activation(data=conv4_3, act_type="relu", name="relu4_3")
    return relu4_3
def get_vgg_conv5_3(relu4_3):
    pool4 = mx.symbol.Pooling(
        data=relu4_3, pool_type="max", kernel=(2, 2), stride=(2, 2), name="pool4")
    # group 5
    conv5_1 = mx.symbol.Convolution(
        data=pool4, kernel=(3, 3), pad=(1, 1), num_filter=512, workspace=2048, name="conv5_1")
    relu5_1 = mx.symbol.Activation(data=conv5_1, act_type="relu", name="relu5_1")
    conv5_2 = mx.symbol.Convolution(
        data=relu5_1, kernel=(3, 3), pad=(1, 1), num_filter=512, workspace=2048, name="conv5_2")
    relu5_2 = mx.symbol.Activation(data=conv5_2, act_type="relu", name="relu5_2")
    conv5_3 = mx.symbol.Convolution(
        data=relu5_2, kernel=(3, 3), pad=(1, 1), num_filter=512, workspace=2048, name="conv5_3")
    relu5_3 = mx.symbol.Activation(data=conv5_3, act_type="relu", name="relu5_3")

    return relu5_3


def get_vgg_rcnn(num_classes=config.NUM_CLASSES):
    """
    Fast R-CNN with VGG 16 conv layers
    :param num_classes: used to determine output size
    :return: Symbol
    """
    data = mx.symbol.Variable(name="data")
    rois = mx.symbol.Variable(name='rois')
    label = mx.symbol.Variable(name='label')
    bbox_target = mx.symbol.Variable(name='bbox_target')
    bbox_weight = mx.symbol.Variable(name='bbox_weight')

    # reshape input
    rois = mx.symbol.Reshape(data=rois, shape=(-1, 5), name='rois_reshape')
    label = mx.symbol.Reshape(data=label, shape=(-1, ), name='label_reshape')
    bbox_target = mx.symbol.Reshape(data=bbox_target, shape=(-1, 4 * num_classes), name='bbox_target_reshape')
    bbox_weight = mx.symbol.Reshape(data=bbox_weight, shape=(-1, 4 * num_classes), name='bbox_weight_reshape')

    # shared convolutional layers
    relu5_3 = get_vgg_conv(data)

    # Fast R-CNN
    pool5 = mx.symbol.ROIPooling(
        name='roi_pool5', data=relu5_3, rois=rois, pooled_size=(7, 7), spatial_scale=1.0 / config.RCNN_FEAT_STRIDE)
    # group 6
    flatten = mx.symbol.Flatten(data=pool5, name="flatten")
    fc6 = mx.symbol.FullyConnected(data=flatten, num_hidden=4096, name="fc6")
    relu6 = mx.symbol.Activation(data=fc6, act_type="relu", name="relu6")
    drop6 = mx.symbol.Dropout(data=relu6, p=0.5, name="drop6")
    # group 7
    fc7 = mx.symbol.FullyConnected(data=drop6, num_hidden=4096, name="fc7")
    relu7 = mx.symbol.Activation(data=fc7, act_type="relu", name="relu7")
    drop7 = mx.symbol.Dropout(data=relu7, p=0.5, name="drop7")
    # classification
    cls_score = mx.symbol.FullyConnected(name='cls_score', data=drop7, num_hidden=num_classes)
    cls_prob = mx.symbol.SoftmaxOutput(name='cls_prob', data=cls_score, label=label, normalization='batch')
    # bounding box regression
    bbox_pred = mx.symbol.FullyConnected(name='bbox_pred', data=drop7, num_hidden=num_classes * 4)
    bbox_loss_ = bbox_weight * mx.symbol.smooth_l1(name='bbox_loss_', scalar=1.0, data=(bbox_pred - bbox_target))
    bbox_loss = mx.sym.MakeLoss(name='bbox_loss', data=bbox_loss_, grad_scale=1.0 / config.TRAIN.BATCH_ROIS)

    # reshape output
    cls_prob = mx.symbol.Reshape(data=cls_prob, shape=(config.TRAIN.BATCH_IMAGES, -1, num_classes), name='cls_prob_reshape')
    bbox_loss = mx.symbol.Reshape(data=bbox_loss, shape=(config.TRAIN.BATCH_IMAGES, -1, 4 * num_classes), name='bbox_loss_reshape')

    # group output
    group = mx.symbol.Group([cls_prob, bbox_loss])
    return group


def get_vgg_rcnn_test(num_classes=config.NUM_CLASSES):
    """
    Fast R-CNN Network with VGG
    :param num_classes: used to determine output size
    :return: Symbol
    """
    data = mx.symbol.Variable(name="data")
    rois = mx.symbol.Variable(name='rois')

    # reshape rois
    rois = mx.symbol.Reshape(data=rois, shape=(-1, 5), name='rois_reshape')

    # shared convolutional layer
    relu5_3 = get_vgg_conv(data)
    
    # Fast R-CNN
    pool5 = mx.symbol.ROIPooling(
        name='roi_pool5', data=relu5_3, rois=rois, pooled_size=(7, 7), spatial_scale=1.0 / config.RCNN_FEAT_STRIDE)
    # group 6
    flatten = mx.symbol.Flatten(data=pool5, name="flatten")
    fc6 = mx.symbol.FullyConnected(data=flatten, num_hidden=4096, name="fc6")
    relu6 = mx.symbol.Activation(data=fc6, act_type="relu", name="relu6")
    drop6 = mx.symbol.Dropout(data=relu6, p=0.5, name="drop6")
    # group 7
    fc7 = mx.symbol.FullyConnected(data=drop6, num_hidden=4096, name="fc7")
    relu7 = mx.symbol.Activation(data=fc7, act_type="relu", name="relu7")
    drop7 = mx.symbol.Dropout(data=relu7, p=0.5, name="drop7")
    # classification
    cls_score = mx.symbol.FullyConnected(name='cls_score', data=drop7, num_hidden=num_classes)
    cls_prob = mx.symbol.SoftmaxOutput(name='cls_prob', data=cls_score)
    # bounding box regression
    bbox_pred = mx.symbol.FullyConnected(name='bbox_pred', data=drop7, num_hidden=num_classes * 4)

    # reshape output
    cls_prob = mx.symbol.Reshape(data=cls_prob, shape=(config.TEST.BATCH_IMAGES, -1, num_classes), name='cls_prob_reshape')
    bbox_pred = mx.symbol.Reshape(data=bbox_pred, shape=(config.TEST.BATCH_IMAGES, -1, 4 * num_classes), name='bbox_pred_reshape')

    # group output
    group = mx.symbol.Group([cls_prob, bbox_pred])
    return group


def get_vgg_rpn(num_anchors=config.NUM_ANCHORS):
    """
    Region Proposal Network with VGG
    :param num_anchors: used to determine output size
    :return: Symbol
    """
    data = mx.symbol.Variable(name="data")
    label = mx.symbol.Variable(name='label')
    bbox_target = mx.symbol.Variable(name='bbox_target')
    bbox_weight = mx.symbol.Variable(name='bbox_weight')

    # shared convolutional layers
    relu3_3 = get_vgg_conv3_3(data)
    relu4_3 = get_vgg_conv4_3(relu3_3)
    relu5_3 = get_vgg_conv(relu4_3)

    # RPN
    rpn_conv = mx.symbol.Convolution(
        data=relu5_3, kernel=(3, 3), pad=(1, 1), num_filter=512, name="rpn_conv_3x3")
    rpn_relu = mx.symbol.Activation(data=rpn_conv, act_type="relu", name="rpn_relu")
    rpn_cls_score = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=2 * num_anchors, name="rpn_cls_score")
    rpn_bbox_pred = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=4 * num_anchors, name="rpn_bbox_pred")

    # prepare rpn data
    rpn_cls_score_reshape = mx.symbol.Reshape(
        data=rpn_cls_score, shape=(0, 2, -1, 0), name="rpn_cls_score_reshape")

    # classification
    cls_prob = mx.symbol.SoftmaxOutput(data=rpn_cls_score_reshape, label=label, multi_output=True,
                                       normalization='valid', use_ignore=True, ignore_label=-1, name="cls_prob")
    # bounding box regression
    bbox_loss_ = bbox_weight * mx.symbol.smooth_l1(name='bbox_loss_', scalar=3.0, data=(rpn_bbox_pred - bbox_target))
    bbox_loss = mx.sym.MakeLoss(name='bbox_loss', data=bbox_loss_, grad_scale=1.0 / config.TRAIN.RPN_BATCH_SIZE)
    # group output
    group = mx.symbol.Group([cls_prob, bbox_loss])
    return group


def get_vgg_rpn_test(num_anchors=config.NUM_ANCHORS):
    """
    Region Proposal Network with VGG
    :param num_anchors: used to determine output size
    :return: Symbol
    """
    data = mx.symbol.Variable(name="data")
    im_info = mx.symbol.Variable(name="im_info")

    # shared convolutional layers
    relu4_3 = get_vgg_conv4_3(data)
    relu5_3 = get_vgg_conv(relu4_3)

    # RPN
    rpn_conv = mx.symbol.Convolution(
        data=relu5_3, kernel=(3, 3), pad=(1, 1), num_filter=512, name="rpn_conv_3x3")
    rpn_relu = mx.symbol.Activation(data=rpn_conv, act_type="relu", name="rpn_relu")
    rpn_cls_score = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=2 * num_anchors, name="rpn_cls_score")
    rpn_bbox_pred = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=4 * num_anchors, name="rpn_bbox_pred")

    # ROI Proposal
    rpn_cls_score_reshape = mx.symbol.Reshape(
        data=rpn_cls_score, shape=(0, 2, -1, 0), name="rpn_cls_score_reshape")
    rpn_cls_prob = mx.symbol.SoftmaxActivation(
        data=rpn_cls_score_reshape, mode="channel", name="rpn_cls_prob")
    rpn_cls_prob_reshape = mx.symbol.Reshape(
        data=rpn_cls_prob, shape=(0, 2 * num_anchors, -1, 0), name='rpn_cls_prob_reshape')
    if config.TEST.CXX_PROPOSAL:
        group = mx.symbol.Proposal(
            cls_prob=rpn_cls_prob_reshape, bbox_pred=rpn_bbox_pred, im_info=im_info, name='rois', output_score=True,
            feature_stride=config.RPN_FEAT_STRIDE, scales=tuple(config.ANCHOR_SCALES), ratios=tuple(config.ANCHOR_RATIOS),
            rpn_pre_nms_top_n=config.TEST.PROPOSAL_PRE_NMS_TOP_N, rpn_post_nms_top_n=config.TEST.PROPOSAL_POST_NMS_TOP_N,
            threshold=config.TEST.PROPOSAL_NMS_THRESH, rpn_min_size=config.TEST.PROPOSAL_MIN_SIZE)
    else:
        group = mx.symbol.Custom(
            cls_prob=rpn_cls_prob_reshape, bbox_pred=rpn_bbox_pred, im_info=im_info, name='rois', output_score=True,
            op_type='proposal', feat_stride=config.RPN_FEAT_STRIDE,
            scales=tuple(config.ANCHOR_SCALES), ratios=tuple(config.ANCHOR_RATIOS),
            rpn_pre_nms_top_n=config.TEST.PROPOSAL_PRE_NMS_TOP_N, rpn_post_nms_top_n=config.TEST.PROPOSAL_POST_NMS_TOP_N,
            threshold=config.TEST.PROPOSAL_NMS_THRESH, rpn_min_size=config.TEST.PROPOSAL_MIN_SIZE)
    # rois = group[0]
    # score = group[1]

    return group


def get_vgg_test(num_classes=config.NUM_CLASSES, num_anchors=config.NUM_ANCHORS):
    """
    Faster R-CNN test with VGG 16 conv layers
    :param num_classes: used to determine output size
    :param num_anchors: used to determine output size
    :return: Symbol
    """
    data = mx.symbol.Variable(name="data")
    im_info = mx.symbol.Variable(name="im_info")

    # shared convolutional layers
    relu3_3 = get_vgg_conv3_3(data)
    relu4_3 = get_vgg_conv4_3(relu3_3)
    relu5_3 = get_vgg_conv5_3(relu4_3)

    # RPN
    rpn_conv = mx.symbol.Convolution(
        data=relu5_3, kernel=(3, 3), pad=(1, 1), num_filter=512, name="rpn_conv_3x3")
    rpn_relu = mx.symbol.Activation(data=rpn_conv, act_type="relu", name="rpn_relu")
    rpn_cls_score = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=2 * num_anchors, name="rpn_cls_score")
    rpn_bbox_pred = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=4 * num_anchors, name="rpn_bbox_pred")

    # ROI Proposal
    rpn_cls_score_reshape = mx.symbol.Reshape(
        data=rpn_cls_score, shape=(0, 2, -1, 0), name="rpn_cls_score_reshape")
    rpn_cls_prob = mx.symbol.SoftmaxActivation(
        data=rpn_cls_score_reshape, mode="channel", name="rpn_cls_prob")
    rpn_cls_prob_reshape = mx.symbol.Reshape(
        data=rpn_cls_prob, shape=(0, 2 * num_anchors, -1, 0), name='rpn_cls_prob_reshape')
    if config.TEST.CXX_PROPOSAL:
        rois = mx.symbol.Proposal(
            cls_prob=rpn_cls_prob_reshape, bbox_pred=rpn_bbox_pred, im_info=im_info, name='rois',
            feature_stride=config.RPN_FEAT_STRIDE, scales=tuple(config.ANCHOR_SCALES), ratios=tuple(config.ANCHOR_RATIOS),
            rpn_pre_nms_top_n=config.TEST.RPN_PRE_NMS_TOP_N, rpn_post_nms_top_n=config.TEST.RPN_POST_NMS_TOP_N,
            threshold=config.TEST.RPN_NMS_THRESH, rpn_min_size=config.TEST.RPN_MIN_SIZE)
    else:
        rois = mx.symbol.Custom(
            cls_prob=rpn_cls_prob_reshape, bbox_pred=rpn_bbox_pred, im_info=im_info, name='rois',
            op_type='proposal', feat_stride=config.RPN_FEAT_STRIDE,
            scales=tuple(config.ANCHOR_SCALES), ratios=tuple(config.ANCHOR_RATIOS),
            rpn_pre_nms_top_n=config.TEST.RPN_PRE_NMS_TOP_N, rpn_post_nms_top_n=config.TEST.RPN_POST_NMS_TOP_N,
            threshold=config.TEST.RPN_NMS_THRESH, rpn_min_size=config.TEST.RPN_MIN_SIZE)

    # Fast R-CNN
    pool5 = mx.symbol.ROIPooling(
        name='roi_pool5', data=relu5_3, rois=rois, pooled_size=(7, 7), spatial_scale=1.0 / config.RCNN_FEAT_STRIDE)
    # group 6
    flatten = mx.symbol.Flatten(data=pool5, name="flatten")
    fc6 = mx.symbol.FullyConnected(data=flatten, num_hidden=4096, name="fc6")
    relu6 = mx.symbol.Activation(data=fc6, act_type="relu", name="relu6")
    drop6 = mx.symbol.Dropout(data=relu6, p=0.5, name="drop6")
    # group 7
    fc7 = mx.symbol.FullyConnected(data=drop6, num_hidden=4096, name="fc7")
    relu7 = mx.symbol.Activation(data=fc7, act_type="relu", name="relu7")
    drop7 = mx.symbol.Dropout(data=relu7, p=0.5, name="drop7")
    # classification
    cls_score = mx.symbol.FullyConnected(name='cls_score', data=drop7, num_hidden=num_classes)
    cls_prob = mx.symbol.SoftmaxOutput(name='cls_prob', data=cls_score)
    # bounding box regression
    bbox_pred = mx.symbol.FullyConnected(name='bbox_pred', data=drop7, num_hidden=num_classes * 4)
    # fixed_group 6
    fixed_flatten = mx.symbol.Flatten(data=pool5, name="fixed_flatten")
    fixed_fc6 = mx.symbol.FullyConnected(data=fixed_flatten, num_hidden=4096, name="fixed_fc6")
    fixed_relu6 = mx.symbol.Activation(data=fixed_fc6, act_type="relu", name="fixed_relu6")
    fixed_drop6 = mx.symbol.Dropout(data=fixed_relu6, p=0.5, name="fixed_drop6")
    # fixed_group 7
    fixed_fc7 = mx.symbol.FullyConnected(data=fixed_drop6, num_hidden=4096, name="fixed_fc7")
    fixed_relu7 = mx.symbol.Activation(data=fixed_fc7, act_type="relu", name="fixed_relu7")
    fixed_drop7 = mx.symbol.Dropout(data=fixed_relu7, p=0.5, name="fixed_drop7")
    # fixed_classification
    fixed_cls_score = mx.symbol.FullyConnected(name='fixed_cls_score', data=fixed_drop7, num_hidden=num_classes)
    #fixed_cls_prob = mx.symbol.SoftmaxOutput(name='fixed_cls_prob', data=fixed_cls_score)
    #cls_prob = mx.symbol.SoftmaxOutput(name='cls_prob', data=fixed_cls_score)
    # fixed_bounding box regression
    fixed_bbox_pred = mx.symbol.FullyConnected(name='fixed_bbox_pred', data=fixed_drop7, num_hidden=num_classes * 4)

    # dfixed_group 6
    dfixed_flatten = mx.symbol.Flatten(data=pool5, name="dfixed_flatten")
    dfixed_fc6 = mx.symbol.FullyConnected(data=dfixed_flatten, num_hidden=4096, name="dfixed_fc6")
    dfixed_relu6 = mx.symbol.Activation(data=dfixed_fc6, act_type="relu", name="dfixed_relu6")
    dfixed_drop6 = mx.symbol.Dropout(data=dfixed_relu6, p=0.5, name="dfixed_drop6")
    # dfixed_group 7
    dfixed_fc7 = mx.symbol.FullyConnected(data=dfixed_drop6, num_hidden=4096, name="dfixed_fc7")
    dfixed_relu7 = mx.symbol.Activation(data=dfixed_fc7, act_type="relu", name="dfixed_relu7")
    dfixed_drop7 = mx.symbol.Dropout(data=dfixed_relu7, p=0.5, name="dfixed_drop7")
    # dfixed_classification
    dfixed_cls_score = mx.symbol.FullyConnected(name='dfixed_cls_score', data=dfixed_drop7, num_hidden=num_classes)
    cls_prob = mx.symbol.SoftmaxOutput(name='cls_prob', data=dfixed_cls_score)
    #dfixed_cls_prob = mx.symbol.SoftmaxOutput(name='dfixed_cls_prob', data=dfixed_cls_score, label=label, normalization='batch')
    # dfixed_bounding box regression
    dfixed_bbox_pred = mx.symbol.FullyConnected(name='dfixed_bbox_pred', data=dfixed_drop7, num_hidden=num_classes * 4)

    # reshape output
    cls_prob = mx.symbol.Reshape(data=cls_prob, shape=(config.TEST.BATCH_IMAGES, -1, num_classes), name='cls_prob_reshape')
    bbox_pred = mx.symbol.Reshape(data=bbox_pred, shape=(config.TEST.BATCH_IMAGES, -1, 4 * num_classes), name='bbox_pred_reshape')
    # fixed_reshape output
    #label = mx.symbol.Reshape(data=label, shape=(config.TRAIN.BATCH_IMAGES, -1), name='label_reshape')
    #fixed_cls_prob = mx.symbol.Reshape(data=fixed_cls_prob, shape=(config.TRAIN.BATCH_IMAGES, -1, num_classes), name='fixed_cls_prob_reshape')
    fixed_bbox_pred = mx.symbol.Reshape(data=fixed_bbox_pred, shape=(config.TEST.BATCH_IMAGES, -1, 4 * num_classes), name='fixed_bbox_pred_reshape')

    # dfixed_reshape output
    #label = mx.symbol.Reshape(data=label, shape=(config.TRAIN.BATCH_IMAGES, -1), name='label_reshape')
    #dfixed_cls_prob = mx.symbol.Reshape(data=dfixed_cls_prob, shape=(config.TRAIN.BATCH_IMAGES, -1, num_classes), name='dfixed_cls_prob_reshape')
    #dfixed_bbox_loss = mx.symbol.Reshape(data=dfixed_bbox_loss, shape=(config.TRAIN.BATCH_IMAGES, -1, 4 * num_classes), name='dfixed_bbox_loss_reshape')
    dfixed_bbox_pred = mx.symbol.Reshape(data=dfixed_bbox_pred, shape=(config.TEST.BATCH_IMAGES, -1, 4 * num_classes), name='dfixed_bbox_pred_reshape')
    # group output
    group = mx.symbol.Group([rois, cls_prob, bbox_pred, dfixed_cls_score, dfixed_bbox_pred])
    #group = mx.symbol.Group([rois, cls_prob, bbox_pred])
    return group


def get_vgg_train(num_classes=config.NUM_CLASSES, num_anchors=config.NUM_ANCHORS):
    """
    Faster R-CNN end-to-end with VGG 16 conv layers
    :param num_classes: used to determine output size
    :param num_anchors: used to determine output size
    :return: Symbol
    """
    data = mx.symbol.Variable(name="data")
    im_info = mx.symbol.Variable(name="im_info")
    gt_boxes = mx.symbol.Variable(name="gt_boxes")
    rpn_label = mx.symbol.Variable(name='label')
    rpn_bbox_target = mx.symbol.Variable(name='bbox_target')
    rpn_bbox_weight = mx.symbol.Variable(name='bbox_weight')

    # shared convolutional layers
    relu3_3 = get_vgg_conv3_3(data)
    relu4_3 = get_vgg_conv4_3(relu3_3)
    relu5_3 = get_vgg_conv5_3(relu4_3)

    # RPN layers
    rpn_conv = mx.symbol.Convolution(
        data=relu5_3, kernel=(3, 3), pad=(1, 1), num_filter=512, name="rpn_conv_3x3")
    rpn_relu = mx.symbol.Activation(data=rpn_conv, act_type="relu", name="rpn_relu")
    rpn_cls_score = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=2 * num_anchors, name="rpn_cls_score")
    rpn_bbox_pred = mx.symbol.Convolution(
        data=rpn_relu, kernel=(1, 1), pad=(0, 0), num_filter=4 * num_anchors, name="rpn_bbox_pred")

    # prepare rpn data
    rpn_cls_score_reshape = mx.symbol.Reshape(
        data=rpn_cls_score, shape=(0, 2, -1, 0), name="rpn_cls_score_reshape")

    # classification
    rpn_cls_prob = mx.symbol.SoftmaxOutput(data=rpn_cls_score_reshape, label=rpn_label, multi_output=True,
                                           normalization='valid', use_ignore=True, ignore_label=-1, name="rpn_cls_prob")
    # bounding box regression
    rpn_bbox_loss_ = rpn_bbox_weight * mx.symbol.smooth_l1(name='rpn_bbox_loss_', scalar=3.0, data=(rpn_bbox_pred - rpn_bbox_target))
    rpn_bbox_loss = mx.sym.MakeLoss(name='rpn_bbox_loss', data=rpn_bbox_loss_, grad_scale=1.0 / config.TRAIN.RPN_BATCH_SIZE)

    # ROI proposal
    rpn_cls_act = mx.symbol.SoftmaxActivation(
        data=rpn_cls_score_reshape, mode="channel", name="rpn_cls_act")
    rpn_cls_act_reshape = mx.symbol.Reshape(
        data=rpn_cls_act, shape=(0, 2 * num_anchors, -1, 0), name='rpn_cls_act_reshape')
    if config.TRAIN.CXX_PROPOSAL:
        rois = mx.symbol.Proposal(
            cls_prob=rpn_cls_act_reshape, bbox_pred=rpn_bbox_pred, im_info=im_info, name='rois',
            feature_stride=config.RPN_FEAT_STRIDE, scales=tuple(config.ANCHOR_SCALES), ratios=tuple(config.ANCHOR_RATIOS),
            rpn_pre_nms_top_n=config.TRAIN.RPN_PRE_NMS_TOP_N, rpn_post_nms_top_n=config.TRAIN.RPN_POST_NMS_TOP_N,
            threshold=config.TRAIN.RPN_NMS_THRESH, rpn_min_size=config.TRAIN.RPN_MIN_SIZE)
    else:
        rois = mx.symbol.Custom(
            cls_prob=rpn_cls_act_reshape, bbox_pred=rpn_bbox_pred, im_info=im_info, name='rois',
            op_type='proposal', feat_stride=config.RPN_FEAT_STRIDE,
            scales=tuple(config.ANCHOR_SCALES), ratios=tuple(config.ANCHOR_RATIOS),
            rpn_pre_nms_top_n=config.TRAIN.RPN_PRE_NMS_TOP_N, rpn_post_nms_top_n=config.TRAIN.RPN_POST_NMS_TOP_N,
            threshold=config.TRAIN.RPN_NMS_THRESH, rpn_min_size=config.TRAIN.RPN_MIN_SIZE)

    # ROI proposal target
    gt_boxes_reshape = mx.symbol.Reshape(data=gt_boxes, shape=(-1, 5), name='gt_boxes_reshape')
    group = mx.symbol.Custom(rois=rois, gt_boxes=gt_boxes_reshape, op_type='proposal_target',
                             num_classes=num_classes, batch_images=config.TRAIN.BATCH_IMAGES,
                             batch_rois=config.TRAIN.BATCH_ROIS, fg_fraction=config.TRAIN.FG_FRACTION)
    rois = group[0]
    label = group[1]
    bbox_target = group[2]
    bbox_weight = group[3]

    # Fast R-CNN
    #roi_pool3 = mx.symbol.ROIPooling(
    #    name='roi_pool3', data=relu3_3, rois=rois, pooled_size=(7, 7), spatial_scale=4.0 / config.RCNN_FEAT_STRIDE)
    #roi_pool4 = mx.symbol.ROIPooling(
     #   name='roi_pool4', data=relu4_3, rois=rois, pooled_size=(7, 7), spatial_scale=2.0 / config.RCNN_FEAT_STRIDE)
    pool5 = mx.symbol.ROIPooling(
        name='roi_pool5', data=relu5_3, rois=rois, pooled_size=(7, 7), spatial_scale=1.0 / config.RCNN_FEAT_STRIDE) 

    #roi_pool3_norm = mx.symbol.L2Normalization(data=roi_pool3, mode="channel")
    #roi_pool4_norm = mx.symbol.L2Normalization(data=roi_pool4, mode="channel")
    #roi_pool5_norm = mx.symbol.L2Normalization(data=roi_pool5, mode="channel")
    #pool5 =  mx.symbol.Concat(roi_pool3_norm, roi_pool4_norm, roi_pool5_norm)
    #pool5_conv = mx.symbol.Convolution(
     #   data=pool5, kernel=(1, 1), pad=(0, 0), num_filter=512, name="pool5_conv_1x1")

    # group 6
    flatten = mx.symbol.Flatten(data=pool5, name="flatten")
    fc6 = mx.symbol.FullyConnected(data=flatten, num_hidden=4096, name="fc6")
    relu6 = mx.symbol.Activation(data=fc6, act_type="relu", name="relu6")
    drop6 = mx.symbol.Dropout(data=relu6, p=0.5, name="drop6")
    # group 7
    fc7 = mx.symbol.FullyConnected(data=drop6, num_hidden=4096, name="fc7")
    relu7 = mx.symbol.Activation(data=fc7, act_type="relu", name="relu7")
    drop7 = mx.symbol.Dropout(data=relu7, p=0.5, name="drop7")
    # classification
    cls_score = mx.symbol.FullyConnected(name='cls_score', data=drop7, num_hidden=num_classes)
    cls_prob = mx.symbol.SoftmaxOutput(name='cls_prob', data=cls_score, label=label, normalization='batch')
    # bounding box regression
    bbox_pred = mx.symbol.FullyConnected(name='bbox_pred', data=drop7, num_hidden=num_classes * 4)
    bbox_loss_ = bbox_weight * mx.symbol.smooth_l1(name='bbox_loss_', scalar=1.0, data=(bbox_pred - bbox_target))
    bbox_loss = mx.sym.MakeLoss(name='bbox_loss', data=bbox_loss_, grad_scale=1.0 / config.TRAIN.BATCH_ROIS)

    # fixed_group 6
    fixed_flatten = mx.symbol.Flatten(data=pool5, name="fixed_flatten")
    fixed_fc6 = mx.symbol.FullyConnected(data=fixed_flatten, num_hidden=4096, name="fixed_fc6")
    fixed_relu6 = mx.symbol.Activation(data=fixed_fc6, act_type="relu", name="fixed_relu6")
    fixed_drop6 = mx.symbol.Dropout(data=fixed_relu6, p=0.5, name="fixed_drop6")
    # fixed_group 7
    fixed_fc7 = mx.symbol.FullyConnected(data=fixed_drop6, num_hidden=4096, name="fixed_fc7")
    fixed_relu7 = mx.symbol.Activation(data=fixed_fc7, act_type="relu", name="fixed_relu7")
    fixed_drop7 = mx.symbol.Dropout(data=fixed_relu7, p=0.5, name="fixed_drop7")
    # fixed_classification
    fixed_cls_score = mx.symbol.FullyConnected(name='fixed_cls_score', data=fixed_drop7, num_hidden=num_classes)
    fixed_cls_prob = mx.symbol.SoftmaxOutput(name='fixed_cls_prob', data=fixed_cls_score, label=label, normalization='batch')
    # fixed_bounding box regression
    fixed_bbox_pred = mx.symbol.FullyConnected(name='fixed_bbox_pred', data=fixed_drop7, num_hidden=num_classes * 4)
    fixed_bbox_loss_ = bbox_weight * mx.symbol.smooth_l1(name='fixed_bbox_loss_', scalar=1.0, data=(fixed_bbox_pred - bbox_target))
    fixed_bbox_loss = mx.sym.MakeLoss(name='fixed_bbox_loss', data=fixed_bbox_loss_, grad_scale=1.0 / config.TRAIN.BATCH_ROIS)

    # dfixed_group 6
    dfixed_flatten = mx.symbol.Flatten(data=pool5, name="dfixed_flatten")
    dfixed_fc6 = mx.symbol.FullyConnected(data=dfixed_flatten, num_hidden=4096, name="dfixed_fc6")
    dfixed_relu6 = mx.symbol.Activation(data=dfixed_fc6, act_type="relu", name="dfixed_relu6")
    dfixed_drop6 = mx.symbol.Dropout(data=dfixed_relu6, p=0.5, name="dfixed_drop6")
    # dfixed_group 7
    dfixed_fc7 = mx.symbol.FullyConnected(data=dfixed_drop6, num_hidden=4096, name="dfixed_fc7")
    dfixed_relu7 = mx.symbol.Activation(data=dfixed_fc7, act_type="relu", name="dfixed_relu7")
    dfixed_drop7 = mx.symbol.Dropout(data=dfixed_relu7, p=0.5, name="dfixed_drop7")
    # dfixed_classification
    dfixed_cls_score = mx.symbol.FullyConnected(name='dfixed_cls_score', data=dfixed_drop7, num_hidden=num_classes)
    dfixed_cls_prob = mx.symbol.SoftmaxOutput(name='dfixed_cls_prob', data=dfixed_cls_score, label=label, normalization='batch')
    # dfixed_bounding box regression
    dfixed_bbox_pred = mx.symbol.FullyConnected(name='dfixed_bbox_pred', data=dfixed_drop7, num_hidden=num_classes * 4)
    dfixed_bbox_loss_ = bbox_weight * mx.symbol.smooth_l1(name='dfixed_bbox_loss_', scalar=1.0, data=(dfixed_bbox_pred - bbox_target))
    dfixed_bbox_loss = mx.sym.MakeLoss(name='dfixed_bbox_loss', data=dfixed_bbox_loss_, grad_scale=1.0 / config.TRAIN.BATCH_ROIS)

    # reshape output
    label = mx.symbol.Reshape(data=label, shape=(config.TRAIN.BATCH_IMAGES, -1), name='label_reshape')
    cls_prob = mx.symbol.Reshape(data=cls_prob, shape=(config.TRAIN.BATCH_IMAGES, -1, num_classes), name='cls_prob_reshape')
    bbox_loss = mx.symbol.Reshape(data=bbox_loss, shape=(config.TRAIN.BATCH_IMAGES, -1, 4 * num_classes), name='bbox_loss_reshape')

    # fixed_reshape output
    #label = mx.symbol.Reshape(data=label, shape=(config.TRAIN.BATCH_IMAGES, -1), name='label_reshape')
    fixed_cls_prob = mx.symbol.Reshape(data=fixed_cls_prob, shape=(config.TRAIN.BATCH_IMAGES, -1, num_classes), name='fixed_cls_prob_reshape')
    fixed_bbox_loss = mx.symbol.Reshape(data=fixed_bbox_loss, shape=(config.TRAIN.BATCH_IMAGES, -1, 4 * num_classes), name='fixed_bbox_loss_reshape')

    # dfixed_reshape output
    #label = mx.symbol.Reshape(data=label, shape=(config.TRAIN.BATCH_IMAGES, -1), name='label_reshape')
    dfixed_cls_prob = mx.symbol.Reshape(data=dfixed_cls_prob, shape=(config.TRAIN.BATCH_IMAGES, -1, num_classes), name='dfixed_cls_prob_reshape')
    dfixed_bbox_loss = mx.symbol.Reshape(data=dfixed_bbox_loss, shape=(config.TRAIN.BATCH_IMAGES, -1, 4 * num_classes), name='dfixed_bbox_loss_reshape')
    group = mx.symbol.Group([rpn_cls_prob, rpn_bbox_loss, dfixed_cls_prob, dfixed_bbox_loss , mx.symbol.BlockGrad(label), cls_prob, bbox_loss, fixed_cls_prob, fixed_bbox_loss])
    #group = mx.symbol.Group([rpn_cls_prob, rpn_bbox_loss, cls_prob, bbox_loss, mx.symbol.BlockGrad(label)])
    return group
