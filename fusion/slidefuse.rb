#! /bos/usr0/yubink/bin/ruby -I /bos/usr0/yubink/rubylib 

module Enumerable
  def stable_sort
    sort_by.with_index { |x, idx| [x, idx] }
  end

  def stable_sort_by
    sort_by.with_index { |x, idx| [yield(x), idx] }
  end
end

class ListData
  attr_accessor :name, :map, :results

  # name: name of retrieval method
  # map: MAP accuracy per query
  # results: hash map from qnum -> list of results
  def initialize(name, map, results)
    @name = name
    @map = map 
    @results = results

    # internal 
    # will be a list of pairs, [[trueMin, qnum], [2ndMin, qnum]], where qnum is source of the min val
    # same, but for max
    @min = [[Float::INFINITY, 0], [Float::INFINITY, 0]]
    @max = [[-Float::INFINITY, 0], [-Float::INFINITY, 0]]

    for qnum, list in results
      if list[-1].score < @min[0][0]
        @min[1] = @min[0]
        @min[0] = [list[-1].score, qnum]
      elsif list[-1].score < @min[1][0]
        @min[1] = [list[-1].score, qnum]
      end

      if list[0].score > @max[0][0]
        @max[1] = @max[0]
        @max[0] = [list[0].score, qnum]
      elsif list[0].score > @max[1][0]
        @max[1] = [list[0].score, qnum]
      end
    end
  end

  # qnum: min of list excluding supplied query number results
  def min(qnum)
    if @min[0][1] != qnum
      return @min[0][0]
    else
      return @min[1][0]
    end
  end

  # qnum: max of list excluding supplied query number results
  def max(qnum)
    if @max[0][1] != qnum
      return @max[0][0]
    else
      return @max[1][0]
    end
  end
end

class SlideFuseMap

  def initialize(window)
    @window = window
    @listweight = Hash.new
    @rankprob = Hash.new
  end

  def train(train_lists, qnums, qrels)
    for list in train_lists
      @listweight = 0

      rankprob_sums = Hash.new(0)
      lst_rankprob = Hash.new(0.0)
      for qnum in qnums
        @listweight += list.map[qnum]

        max = list.max(qnum)
        min = list.min(qnum)

        for row in list.results[qnum]
          #normalize rank list scores with MinMaxNorm
          norm_score = (row.score - min) / (max - min)
          if qrels[qnum].has_key?(row.docno) && qrels[qnum][row.docno] > 0
            lst_rankprob[row.rank] += 1
          end
          rankprob_sums[row.rank] += 1
        end
      end

      for rank, sum in rankprob_sums
        lst_rankprob[rank] /= sum
      end

      @rankprob[list.name] = lst_rankprob
      @listweight /= qnums.size.to_f
    end
  end

  def fuse(fuse_lists, qnums)
    #rank_limit = 1000
    rank_limit = 0

    all_fused = Hash.new
    for qnum in qnums
      docscores = Hash.new(0)
      for list in fuse_lists
        max_rank = list.results[qnum].size
        if rank_limit > 0
          max_rank = rank_limit
        end

        for row in list.results[qnum]
          if rank_limit > 0 && row.rank > rank_limit
            break
          end
          a = row.rank < @window ? 0 : row.rank - @window
          b = row.rank + @window > max_rank ? max_rank : row.rank + @window

          slidesum = 0
          for i in a..b
            slidesum = @rankprob[list.name][i]
          end

          docscores[row.docno] += slidesum / (b-a+1)
        end
      end

      sorted_scores = docscores.to_a.sort {|x,y| y[1] <=> x[1]}
      rows = []
      rank = 1
      for docno, score in sorted_scores
        rows << IRMetrics::ResultRow.new(qnum, docno, rank, score)
        rank += 1
      end
      all_fused[qnum] = rows
    end

    return all_fused
  end
end
