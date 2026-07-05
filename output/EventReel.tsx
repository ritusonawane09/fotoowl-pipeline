import React from 'react';
import {AbsoluteFill, Composition, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';

export const EventReel: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{backgroundColor: 'black'}}>
      <Sequence from=0 durationInFrames=135>
        <AbsoluteFill style={{backgroundColor: 'black'}}>
          <Img
            src={staticFile("input_images/DSC_6596.jpg")}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - 0, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          />
          {"" && (
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}
            >
              <div>{""}</div>
            </AbsoluteFill>
          )}
        </AbsoluteFill>
      </Sequence>
      <Sequence from=135 durationInFrames=135>
        <AbsoluteFill style={{backgroundColor: 'black'}}>
          <Img
            src={staticFile("input_images/DSC_6588.jpg")}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - 135, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          />
          {"" && (
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}
            >
              <div>{""}</div>
            </AbsoluteFill>
          )}
        </AbsoluteFill>
      </Sequence>
      <Sequence from=270 durationInFrames=135>
        <AbsoluteFill style={{backgroundColor: 'black'}}>
          <Img
            src={staticFile("input_images/DSC_6605.jpg")}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              opacity: interpolate(frame - 270, [0, 20], [0, 1], {extrapolateRight: 'clamp'}),
            }}
          />
          {"" && (
            <AbsoluteFill
              style={{
                justifyContent: 'flex-end',
                alignItems: 'center',
                paddingBottom: 90,
                color: 'white',
                fontSize: 44,
                fontFamily: 'sans-serif',
                textShadow: '0 3px 12px rgba(0,0,0,0.65)',
              }}
            >
              <div>{""}</div>
            </AbsoluteFill>
          )}
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="EventReel"
      component={EventReel}
      durationInFrames=405
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
