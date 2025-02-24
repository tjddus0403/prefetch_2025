from setting import *
import torch.optim as optim
from tqdm import tqdm
from dataLoader import *
from model import *
from ast import literal_eval
from torchinfo import summary


def model_arch(model):
    summary(model, input_size=(args.batch_size, 128))

def idx_to_toklist(list_):
    voc = vectorizer.pa_vocab
    result=[]
    for idx in list_:
        result.append(voc.lookup_index(idx))
    return result

def str_to_list(strlist):
    return literal_eval(strlist)

def idx_to_tok(idx):
    voc = vectorizer.pa_vocab
    return voc.lookup_index(idx)

def idx2addr(result_idx):
    # result_idx = pd.read_csv(f"./results/{trace}_test_result_idx.csv")
    result_idx['pred'] = result_idx['pred'].apply(str_to_list)
    result_idx['pred'] = result_idx['pred'].apply(idx_to_toklist)
    result_idx['target'] = result_idx['target'].apply(idx_to_tok)
    result_idx.to_csv(f"./results/clstm_leap/{trace}_test_result_addr.csv", index=False)

def test(dataset, model):
    result_df = pd.DataFrame()
    dataset.set_split('test')
    test_batch_generator = generate_batches(dataset, batch_size=1, device=args.device)
    test_iterator = tqdm(test_batch_generator, desc="Test (X / X Steps)", dynamic_ncols=True)
    test_total = dataset.get_num_batches(1)
    correct = 0
    with torch.no_grad():
        for idx, data in enumerate(test_iterator):
            output = model(data['x_data'].to(args.device))
            topk_vals, topk_indices = torch.topk(output, 10)
            toplist = topk_indices.detach().cpu().tolist()
            target = data['y_target'].squeeze().cpu().detach().numpy()
            output_df = pd.DataFrame({'pred':[toplist], 'target':target})
            result_df = pd.concat([result_df, output_df])
            if target in toplist:
                correct+=1
            test_iterator.set_description("Test (%d / %d Steps)" %(idx, test_total))
    # print(correct)
    print("Accuracy:", correct/test_total*100)
    # result_df.to_csv(f'./results/{trace}_test_result_idx.csv', index=False)
    idx2addr(result_df)

if __name__=='__main__':
    set_seed_everywhere(args.seed, args.cuda)
    dataset_df = load_data("train/val")
    vocabset_df = load_data("vocab")
    testset_df = load_data("test")

    # 현재 사용가능한 디바이스로 환경변수 device 재설정
    args.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(args.device)
    # 학습에 사용할 데이터셋 파일 가져와서 Dataset 객체 만들기 
    dataset = CstateDataset.load_dataset_and_make_vectorizer(dataset_df, vocabset_df, testset_df, args.train_cstate_len, args.data_cstate_len - args.train_cstate_len)
    vectorizer = dataset.get_vectorizer()

    model = Prefetcher(args, len(vectorizer.pa_vocab)).to(args.device)
   
    model.load_state_dict(torch.load(f'./models/{trace}/model_20.pth'))
    model = model.to(args.device)

    # 모델 구조 및 사이즈 측정
    # model_arch(model)

    test(dataset, model)